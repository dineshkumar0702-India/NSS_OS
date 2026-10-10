from fastapi import APIRouter, Depends

from nasd.audit import audit_log
from nasd.deps import DbDep, require_role
from nasd.errors import Problem
from nasd.models import User
from nasd.schemas import UserCreate, UserPublic, UserUpdate
from nasd.security import hash_password, role_at_least

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users(db: DbDep, _user: User = Depends(require_role("operator"))) -> dict:
    users = db.query(User).order_by(User.username).all()
    return {
        "items": [
            UserPublic(id=u.id, username=u.username, role=u.role, display_name=u.display_name)
            for u in users
        ]
    }


@router.post("", response_model=UserPublic)
def create_user(
    body: UserCreate,
    db: DbDep,
    actor: User = Depends(require_role("admin")),
) -> User:
    if db.query(User).filter(User.username == body.username).first():
        raise Problem(409, "Exists", "username taken", "VALIDATION_ERROR")
    if not role_at_least(actor.role, body.role) and actor.role != "owner":
        raise Problem(403, "Forbidden", "cannot assign higher role", "AUTH_FAILED")
    user = User(
        username=body.username,
        display_name=body.display_name or body.username,
        role=body.role,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    audit_log(db, actor_user_id=actor.id, action="users.create", outcome="success", target_id=user.id)
    db.commit()
    db.refresh(user)
    return UserPublic(id=user.id, username=user.username, role=user.role, display_name=user.display_name)


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: str,
    body: UserUpdate,
    db: DbDep,
    actor: User = Depends(require_role("admin")),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise Problem(404, "Not found", "user not found", "NOT_FOUND")
    if body.display_name is not None:
        user.display_name = body.display_name
    if body.role is not None:
        user.role = body.role
    if body.password is not None:
        user.password_hash = hash_password(body.password)
    audit_log(db, actor_user_id=actor.id, action="users.update", outcome="success", target_id=user.id)
    db.commit()
    return UserPublic(id=user.id, username=user.username, role=user.role, display_name=user.display_name)


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: DbDep,
    actor: User = Depends(require_role("admin")),
) -> dict:
    user = db.get(User, user_id)
    if user is None:
        raise Problem(404, "Not found", "user not found", "NOT_FOUND")
    if user.role == "owner":
        raise Problem(400, "Protected", "cannot delete owner", "VALIDATION_ERROR")
    db.delete(user)
    audit_log(db, actor_user_id=actor.id, action="users.delete", outcome="success", target_id=user_id)
    db.commit()
    return {"status": "deleted"}
