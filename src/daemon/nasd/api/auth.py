from fastapi import APIRouter, Cookie, Depends, Response

from nasd.audit import audit_log
from nasd.deps import DbDep, get_current_user
from nasd.models import AuthSession, User
from nasd.schemas import LoginRequest, UserPublic
from nasd.security import hash_token, new_session_id, session_expiry, verify_password
from nasd.settings import settings

login_router = APIRouter(prefix="/auth", tags=["auth"])
session_router = APIRouter(prefix="/auth", tags=["auth"])


@login_router.post("/login", response_model=UserPublic)
def login(body: LoginRequest, response: Response, db: DbDep) -> User:
    user = db.query(User).filter(User.username == body.username).first()
    if user is None or not user.password_hash or not verify_password(user.password_hash, body.password):
        audit_log(db, actor_user_id=None, action="auth.login", outcome="denied")
        db.commit()
        from nasd.errors import Problem

        raise Problem(401, "Login failed", "invalid credentials", "AUTH_FAILED")
    sid = new_session_id()
    db.add(
        AuthSession(
            id=hash_token(sid),
            user_id=user.id,
            expires_at=session_expiry(settings.session_ttl_hours),
            ip=None,
            user_agent=None,
        )
    )
    audit_log(db, actor_user_id=user.id, action="auth.login", outcome="success")
    db.commit()
    response.set_cookie(
        key=settings.cookie_name,
        value=sid,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        max_age=settings.session_ttl_hours * 3600,
    )
    return user


@session_router.post("/logout")
def logout(
    response: Response,
    db: DbDep,
    user: User = Depends(get_current_user),
    nas_session: str | None = Cookie(default=None, alias=settings.cookie_name),
) -> dict:
    if nas_session:
        row = db.get(AuthSession, hash_token(nas_session))
        if row:
            db.delete(row)
    response.delete_cookie(settings.cookie_name)
    audit_log(db, actor_user_id=user.id, action="auth.logout", outcome="success")
    db.commit()
    return {"status": "ok"}


@session_router.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)) -> User:
    return user
