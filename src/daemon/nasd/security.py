import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher()


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def new_session_id() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def new_api_token() -> str:
    return f"onl_{secrets.token_urlsafe(32)}"


def session_expiry(hours: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=hours)
    return exp.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def is_expired(iso_ts: str) -> bool:
    try:
        if iso_ts.endswith("Z"):
            iso_ts = iso_ts[:-1] + "+00:00"
        return datetime.fromisoformat(iso_ts) <= datetime.now(timezone.utc)
    except ValueError:
        return True


ROLE_ORDER = {"viewer": 0, "operator": 1, "admin": 2, "owner": 3}


def role_at_least(role: str, minimum: str) -> bool:
    return ROLE_ORDER.get(role, -1) >= ROLE_ORDER.get(minimum, 99)
