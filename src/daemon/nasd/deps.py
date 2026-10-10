import json
from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from nasd.database import get_db
from nasd.errors import Problem
from nasd.models import ApiToken, AuthSession, SystemConfig, User
from nasd.security import hash_token, is_expired, role_at_least
from nasd.settings import settings

DbDep = Annotated[Session, Depends(get_db)]


def _user_from_session(db: Session, session_id: str | None) -> User | None:
    if not session_id:
        return None
    sid_hash = hash_token(session_id)
    row = db.get(AuthSession, sid_hash)
    if row is None or is_expired(row.expires_at):
        return None
    return db.get(User, row.user_id)


def _user_from_bearer(db: Session, authorization: str | None) -> User | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    th = hash_token(token)
    row = db.query(ApiToken).filter(ApiToken.token_hash == th).first()
    if row is None:
        return None
    return db.get(User, row.user_id)


def get_current_user_optional(
    request: Request,
    db: DbDep,
    authorization: Annotated[str | None, Header()] = None,
) -> User | None:
    user = _user_from_bearer(db, authorization)
    if user:
        return user
    nas_session = request.cookies.get(settings.cookie_name)
    if nas_session:
        return _user_from_session(db, nas_session)
    return None


def get_current_user(user: Annotated[User | None, Depends(get_current_user_optional)]) -> User:
    if user is None:
        raise Problem(401, "Unauthorized", "authentication required", "AUTH_FAILED")
    return user


def require_role(minimum: str):
    def _checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if not role_at_least(user.role, minimum):
            raise Problem(403, "Forbidden", "insufficient role", "AUTH_FAILED")
        return user

    return _checker


def setup_complete(db: Session) -> bool:
    row = db.get(SystemConfig, "setup_complete")
    if row is None:
        return False
    try:
        return bool(json.loads(row.value_json))
    except json.JSONDecodeError:
        return row.value_json.lower() == "true"


def require_setup_complete(db: DbDep, request: Request) -> None:
    path = request.url.path
    if path in ("/api/v1/system/status", "/api/v1/system/setup", "/api/v1/auth/login"):
        return
    if path == "/healthz":
        return
    if not setup_complete(db):
        raise Problem(503, "Setup required", "complete first-boot setup first", "VALIDATION_ERROR")
