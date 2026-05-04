"""
Authentication service for DeepTutor.

Disabled by default (AUTH_ENABLED=false) so localhost users are unaffected.
When enabled, guards all API routes with JWT bearer tokens.

Quick setup (single user via env vars):
    1. Set AUTH_ENABLED=true in .env
    2. Set AUTH_USERNAME=<your username>
    3. Generate a password hash:
           python -c "from deeptutor.services.auth import hash_password; print(hash_password('yourpassword'))"
       Paste the output into AUTH_PASSWORD_HASH=<hash>
    4. Set AUTH_SECRET to a long random string

Multi-user setup (recommended):
    Enable AUTH_ENABLED=true and leave AUTH_USERNAME/AUTH_PASSWORD_HASH empty.
    Navigate to /register in the browser. The first user to register is granted
    admin privileges and can manage other users from /admin/users.

    Users are stored in data/user/auth_users.json:
        {
            "alice": {"hash": "$2b$12$...", "role": "admin", "created_at": "2026-..."},
            "bob":   {"hash": "$2b$12$...", "role": "user",  "created_at": "2026-..."}
        }
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import logging
import os
from pathlib import Path
import secrets

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — read once at import time
# ---------------------------------------------------------------------------

AUTH_ENABLED: bool = os.getenv("AUTH_ENABLED", "false").lower() == "true"
AUTH_USERNAME: str = os.getenv("AUTH_USERNAME", "admin")
AUTH_PASSWORD_HASH: str = os.getenv("AUTH_PASSWORD_HASH", "")
AUTH_SECRET: str = os.getenv("AUTH_SECRET", "")
TOKEN_EXPIRE_HOURS: int = int(os.getenv("AUTH_TOKEN_EXPIRE_HOURS", "24"))

# PocketBase auth mode — active when POCKETBASE_URL is set AND AUTH_ENABLED=true.
# When enabled, login/register proxy to PocketBase and token validation uses
# PocketBase's auth-refresh endpoint (cached in memory — no static secret needed).
POCKETBASE_URL: str = os.getenv("POCKETBASE_URL", "").rstrip("/")
POCKETBASE_ENABLED: bool = bool(POCKETBASE_URL) and AUTH_ENABLED

_ALGORITHM = "HS256"
_USERS_FILE = Path("data/user/auth_users.json")

if AUTH_ENABLED and not POCKETBASE_ENABLED and not AUTH_SECRET:
    logger.warning(
        "AUTH_ENABLED=true but AUTH_SECRET is not set. "
        "A temporary secret will be generated — tokens will be invalidated on restart. "
        "Set AUTH_SECRET in .env to a stable random value."
    )
    AUTH_SECRET = secrets.token_hex(32)


# ---------------------------------------------------------------------------
# Token payload
# ---------------------------------------------------------------------------


@dataclass
class TokenPayload:
    """Decoded JWT payload."""

    username: str
    role: str


# ---------------------------------------------------------------------------
# Password hashing — uses bcrypt directly (passlib is unmaintained for bcrypt 4+)
# ---------------------------------------------------------------------------


def hash_password(plain: str) -> str:
    """Hash a plaintext password. Use this to generate password hashes."""
    import bcrypt

    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    import bcrypt

    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


# ---------------------------------------------------------------------------
# User store — JSON file takes priority over env vars
# ---------------------------------------------------------------------------


def _make_user_record(hashed: str, role: str = "user", created_at: str = "") -> dict:
    """Build a canonical user record dict."""
    return {
        "hash": hashed,
        "role": role,
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
    }


def _load_users() -> dict[str, dict]:
    """
    Load the user store, migrating old flat format if needed.

    Priority:
      1. data/user/auth_users.json — multi-user file
      2. AUTH_USERNAME + AUTH_PASSWORD_HASH env vars — single-user fallback

    Old format: {"alice": "$2b$12$..."}
    New format: {"alice": {"hash": "...", "role": "admin", "created_at": "..."}}
    """
    if _USERS_FILE.exists():
        try:
            data = json.loads(_USERS_FILE.read_text())
            if not isinstance(data, dict):
                logger.warning("auth_users.json is not a JSON object — falling back to env vars")
                data = {}

            migrated = False
            users: dict[str, dict] = {}
            for username, value in data.items():
                if isinstance(value, str):
                    # Migrate old flat hash string — first user in old file gets admin
                    role = "admin" if not users else "user"
                    users[username] = _make_user_record(value, role=role)
                    migrated = True
                elif isinstance(value, dict):
                    users[username] = value
                else:
                    logger.warning(f"Skipping malformed user entry: {username!r}")

            if migrated:
                _USERS_FILE.write_text(json.dumps(users, indent=2))
                logger.info("Migrated auth_users.json to new schema with role/created_at fields")

            return users
        except Exception as exc:
            logger.warning(f"Failed to read auth_users.json: {exc} — falling back to env vars")

    # Env-var single-user fallback — always treated as admin
    if AUTH_USERNAME and AUTH_PASSWORD_HASH:
        return {AUTH_USERNAME: _make_user_record(AUTH_PASSWORD_HASH, role="admin", created_at="")}

    return {}


def is_first_user() -> bool:
    """Return True when no users exist yet (first registration will become admin)."""
    return len(_load_users()) == 0


def add_user(username: str, plain_password: str, role: str = "user") -> None:
    """
    Add or update a user in data/user/auth_users.json.

    The role defaults to 'user'. Pass role='admin' to elevate. When the store
    is empty the first user is automatically promoted to 'admin' regardless of
    the role argument.

    Creates the file (and parent directories) if they don't exist.
    """
    _USERS_FILE.parent.mkdir(parents=True, exist_ok=True)

    users: dict[str, dict] = {}
    if _USERS_FILE.exists():
        try:
            users = json.loads(_USERS_FILE.read_text())
        except Exception:
            pass

    effective_role = "admin" if not users else role
    users[username] = _make_user_record(hash_password(plain_password), role=effective_role)
    _USERS_FILE.write_text(json.dumps(users, indent=2))
    logger.info(f"User '{username}' saved to {_USERS_FILE} with role={effective_role!r}")


def list_users() -> list[dict]:
    """Return a list of user info dicts (username, role, created_at) — no hashes."""
    users = _load_users()
    return [
        {
            "username": username,
            "role": record.get("role", "user"),
            "created_at": record.get("created_at", ""),
        }
        for username, record in users.items()
    ]


def delete_user(username: str) -> bool:
    """
    Remove a user from the store. Returns True if the user existed.

    Note: env-var-only users cannot be deleted via this function.
    """
    if not _USERS_FILE.exists():
        return False

    try:
        users: dict[str, dict] = json.loads(_USERS_FILE.read_text())
    except Exception:
        return False

    if username not in users:
        return False

    del users[username]
    _USERS_FILE.write_text(json.dumps(users, indent=2))
    logger.info(f"User '{username}' deleted from {_USERS_FILE}")
    return True


def set_role(username: str, role: str) -> bool:
    """
    Change the role for an existing user. Returns True on success.

    Valid roles: 'admin', 'user'.
    """
    if role not in ("admin", "user"):
        raise ValueError(f"Invalid role: {role!r}. Must be 'admin' or 'user'.")

    if not _USERS_FILE.exists():
        return False

    try:
        users: dict[str, dict] = json.loads(_USERS_FILE.read_text())
    except Exception:
        return False

    if username not in users:
        return False

    users[username]["role"] = role
    _USERS_FILE.write_text(json.dumps(users, indent=2))
    logger.info(f"User '{username}' role updated to {role!r}")
    return True


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------


def create_token(username: str, role: str = "user") -> str:
    """Create a signed JWT for the given username and role."""
    from jose import jwt

    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, AUTH_SECRET, algorithm=_ALGORITHM)


def decode_token(token: str) -> TokenPayload | None:
    """
    Validate a token and return a TokenPayload, or None if invalid.

    - PocketBase mode: calls PocketBase's auth-refresh endpoint (cached in
      memory for 60 s, so only the first request per token per minute makes
      a network call). No static JWT secret required.
    - Standard mode: local in-memory jwt.decode() using AUTH_SECRET — zero
      network calls, same as before.
    """
    if not token:
        return None

    if POCKETBASE_ENABLED:
        from deeptutor.services.pocketbase_client import validate_pb_token

        payload = validate_pb_token(token)
        if payload is None:
            return None
        return TokenPayload(
            username=payload["username"],
            role=payload.get("role", "user"),
        )

    # Standard JWT + bcrypt mode
    from jose import JWTError, jwt

    if not AUTH_SECRET:
        return None

    try:
        payload = jwt.decode(token, AUTH_SECRET, algorithms=[_ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
        return TokenPayload(username=username, role=payload.get("role", "user"))
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# PocketBase auth helpers
# ---------------------------------------------------------------------------


def authenticate_pb(username: str, password: str) -> tuple[TokenPayload, str] | None:
    """
    Authenticate against PocketBase and return (TokenPayload, raw_pb_token).

    Only called when POCKETBASE_ENABLED=True.
    Returns None on failure.
    The raw token is the PocketBase JWT string to be stored in the cookie.

    PocketBase requires an email address; plain usernames are mapped to
    <username>@deeptutor.local to match the email used at registration.
    """
    try:
        from deeptutor.services.pocketbase_client import get_pb_client

        pb = get_pb_client()
        result = pb.collection("users").auth_with_password(username, password)
        token: str = result.token
        record = result.record
        username = (
            getattr(record, "email", None)
            or getattr(record, "name", None)
            or getattr(record, "id", "unknown")
        )
        # PocketBase has no built-in "role" field by default; treat all as "user".
        # Admins authenticated via PocketBase admin panel use a separate endpoint.
        role = getattr(record, "role", "user") or "user"
        return TokenPayload(username=str(username), role=str(role)), token
    except Exception as exc:
        logger.warning(f"PocketBase authentication failed: {exc}")
        return None


def register_pb(username: str, email: str, password: str) -> dict | None:
    """
    Create a new user in PocketBase.

    Returns the created user record dict or None on failure.
    """
    try:
        from deeptutor.services.pocketbase_client import get_pb_client

        pb = get_pb_client()
        record = pb.collection("users").create(
            {
                "username": username,
                "email": email,
                "password": password,
                "passwordConfirm": password,
            }
        )
        return {"id": record.id, "username": username, "email": email}
    except Exception as exc:
        logger.warning(f"PocketBase registration failed: {exc}")
        return None


# ---------------------------------------------------------------------------
# Main auth entry point
# ---------------------------------------------------------------------------


def authenticate(username: str, password: str) -> TokenPayload | None:
    """
    Validate credentials. Returns a TokenPayload on success, None on failure.

    When AUTH_ENABLED=false, always returns a dummy admin payload so that
    callers don't need to special-case the disabled state.
    """
    if not AUTH_ENABLED:
        return TokenPayload(username=username or "local", role="admin")

    users = _load_users()
    if not users:
        logger.warning(
            "No users configured — login will always fail. "
            "Navigate to /register to create your first account."
        )
        return None

    record = users.get(username)
    if not record:
        return None

    hashed = record.get("hash", "") if isinstance(record, dict) else record
    if not verify_password(password, hashed):
        return None

    role = record.get("role", "user") if isinstance(record, dict) else "user"
    return TokenPayload(username=username, role=role)
