"""Auth router — login, logout, status, registration, and user-management endpoints."""

import logging
import os

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, field_validator

# SameSite=None lets the cookie work when the browser accesses the frontend via
# 127.0.0.1 and the backend via localhost (different origins on the same machine).
# Browsers require Secure=True for SameSite=None, but that needs HTTPS — so in
# local dev we fall back to SameSite=Lax and tell users to use localhost:// URLs.
_SECURE = os.getenv("AUTH_COOKIE_SECURE", "false").lower() == "true"
_SAMESITE = "none" if _SECURE else "lax"

from deeptutor.services.auth import (
    AUTH_ENABLED,
    POCKETBASE_ENABLED,
    TOKEN_EXPIRE_HOURS,
    TokenPayload,
    add_user,
    authenticate,
    authenticate_pb,
    create_token,
    decode_token,
    delete_user,
    is_first_user,
    list_users,
    register_pb,
    set_role,
)

logger = logging.getLogger(__name__)

router = APIRouter()
_bearer = HTTPBearer(auto_error=False)

_COOKIE_NAME = "dt_token"
_COOKIE_MAX_AGE = TOKEN_EXPIRE_HOURS * 3600


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    """Payload for the POST /login endpoint."""

    username: str
    password: str


class RegisterRequest(BaseModel):
    """Payload for the POST /register endpoint."""

    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        import re

        v = v.strip()
        if not v:
            raise ValueError("Email cannot be empty")
        # Accept standard email addresses (used by PocketBase mode) or plain
        # usernames (used by the built-in SQLite/JSON auth mode).
        email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        plain_re = re.compile(r"^[A-Za-z0-9_\-.]{3,64}$")
        if not email_re.match(v) and not plain_re.match(v):
            raise ValueError("Enter a valid email address")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class SetRoleRequest(BaseModel):
    """Payload for the PUT /users/{username}/role endpoint."""

    role: str

    @field_validator("role")
    @classmethod
    def role_valid(cls, v: str) -> str:
        if v not in ("admin", "user"):
            raise ValueError("Role must be 'admin' or 'user'")
        return v


class AuthStatusResponse(BaseModel):
    """Response body for the GET /status endpoint."""

    enabled: bool
    authenticated: bool
    username: str | None = None
    role: str | None = None


class UserInfo(BaseModel):
    """Single user record returned by the GET /users endpoint."""

    username: str
    role: str
    created_at: str


# ---------------------------------------------------------------------------
# Shared helper — extract token from cookie or Bearer header
# ---------------------------------------------------------------------------


def _extract_token(
    credentials: HTTPAuthorizationCredentials | None,
    dt_token: str | None,
) -> str | None:
    if credentials:
        return credentials.credentials
    return dt_token


# ---------------------------------------------------------------------------
# Dependencies — reusable auth guards for other routers
# ---------------------------------------------------------------------------


def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    dt_token: str | None = Cookie(default=None),
) -> TokenPayload | None:
    """
    FastAPI dependency that enforces authentication when AUTH_ENABLED=true.

    Accepts the JWT from either:
      - Authorization: Bearer <token> header
      - dt_token cookie

    Returns the authenticated TokenPayload, or None if auth is disabled.
    Raises HTTP 401 if auth is enabled but the token is missing or invalid.
    """
    if not AUTH_ENABLED:
        return None

    token = _extract_token(credentials, dt_token)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def require_admin(
    payload: TokenPayload | None = Depends(require_auth),
) -> TokenPayload:
    """
    FastAPI dependency that requires the caller to be an admin.

    Raises HTTP 403 if the authenticated user is not an admin.
    When AUTH_ENABLED=false, all requests are treated as admin.
    """
    if not AUTH_ENABLED:
        from deeptutor.services.auth import TokenPayload as TP

        return TP(username="local", role="admin")

    if payload is None or payload.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return payload


# ---------------------------------------------------------------------------
# Public endpoints (no auth required)
# ---------------------------------------------------------------------------


@router.get("/status", response_model=AuthStatusResponse)
async def auth_status(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    dt_token: str | None = Cookie(default=None),
) -> AuthStatusResponse:
    """Return whether auth is enabled and whether the current request is authenticated."""
    if not AUTH_ENABLED:
        return AuthStatusResponse(enabled=False, authenticated=True, role="admin")

    token = _extract_token(credentials, dt_token)
    payload = decode_token(token) if token else None
    return AuthStatusResponse(
        enabled=True,
        authenticated=payload is not None,
        username=payload.username if payload else None,
        role=payload.role if payload else None,
    )


@router.post("/login")
async def login(body: LoginRequest, response: Response) -> dict:
    """Validate credentials and set a JWT cookie."""
    if not AUTH_ENABLED:
        return {"ok": True, "message": "Auth is disabled — no login required."}

    if POCKETBASE_ENABLED:
        # PocketBase mode: email = username field for backwards-compat with the
        # existing LoginRequest schema; users can pass their email as "username".
        pb_result = authenticate_pb(body.username, body.password)
        if not pb_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        payload, pb_token = pb_result
        response.set_cookie(
            key=_COOKIE_NAME,
            value=pb_token,
            httponly=True,
            samesite=_SAMESITE,
            max_age=_COOKIE_MAX_AGE,
            secure=_SECURE,
        )
        logger.info(f"User '{payload.username}' logged in via PocketBase (role={payload.role!r})")
        return {"ok": True, "username": payload.username, "role": payload.role}

    # Standard JWT + bcrypt mode
    result = authenticate(body.username, body.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_token(result.username, result.role)
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite=_SAMESITE,
        max_age=_COOKIE_MAX_AGE,
        secure=_SECURE,
    )

    logger.info(f"User '{result.username}' logged in (role={result.role!r})")
    return {"ok": True, "username": result.username, "role": result.role}


@router.post("/logout")
async def logout(response: Response) -> dict:
    """Clear the JWT cookie."""
    response.delete_cookie(key=_COOKIE_NAME, samesite=_SAMESITE)
    return {"ok": True}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest) -> dict:
    """
    Create a new user account.

    In PocketBase mode, the username is also used as the email address.
    In standard mode, the first user to register is automatically granted admin.

    Only available when AUTH_ENABLED=true.
    """
    if not AUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Auth is disabled — registration is not available.",
        )

    if POCKETBASE_ENABLED:
        result = register_pb(username=body.username, email=body.username, password=body.password)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Registration failed — username or email may already be taken.",
            )
        logger.info(f"New user registered via PocketBase: '{body.username}'")
        return {"ok": True, "username": body.username, "role": "user", "is_first_user": False}

    # Standard mode
    first = is_first_user()
    existing = {u["username"] for u in list_users()}
    if body.username in existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    add_user(body.username, body.password)
    role = "admin" if first else "user"
    logger.info(f"New user registered: '{body.username}' (role={role!r})")
    return {"ok": True, "username": body.username, "role": role, "is_first_user": first}


@router.get("/is_first_user")
async def check_is_first_user() -> dict:
    """Return whether the user store is empty (used by the register UI)."""
    return {"is_first_user": is_first_user() if AUTH_ENABLED else False}


# ---------------------------------------------------------------------------
# Admin-only endpoints
# ---------------------------------------------------------------------------


@router.get("/users", response_model=list[UserInfo])
async def get_users(_: TokenPayload = Depends(require_admin)) -> list[UserInfo]:
    """List all registered users. Requires admin role."""
    return [UserInfo(**u) for u in list_users()]


@router.delete("/users/{username}", status_code=status.HTTP_200_OK)
async def remove_user(
    username: str,
    current: TokenPayload = Depends(require_admin),
) -> dict:
    """Delete a user. Admins cannot delete their own account."""
    if current and username == current.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    removed = delete_user(username)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    logger.info(f"Admin '{current.username if current else 'local'}' deleted user '{username}'")
    return {"ok": True}


@router.put("/users/{username}/role", status_code=status.HTTP_200_OK)
async def update_user_role(
    username: str,
    body: SetRoleRequest,
    current: TokenPayload = Depends(require_admin),
) -> dict:
    """Change a user's role. Admins cannot change their own role."""
    if current and username == current.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role",
        )

    updated = set_role(username, body.role)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    logger.info(
        f"Admin '{current.username if current else 'local'}' set '{username}' role to {body.role!r}"
    )
    return {"ok": True, "username": username, "role": body.role}
