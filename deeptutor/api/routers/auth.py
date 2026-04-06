"""Auth router — login, logout, status, registration, and user-management endpoints."""

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, field_validator

from deeptutor.logging import get_logger
from deeptutor.services.auth import (
    AUTH_ENABLED,
    TOKEN_EXPIRE_HOURS,
    TokenPayload,
    add_user,
    authenticate,
    create_token,
    decode_token,
    delete_user,
    is_first_user,
    list_users,
    set_role,
)

logger = get_logger("Auth")

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
        v = v.strip()
        if not v:
            raise ValueError("Username cannot be empty")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 32:
            raise ValueError("Username must be at most 32 characters")
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.")
        if not all(c in allowed for c in v):
            raise ValueError("Username may only contain letters, digits, -, _, and .")
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
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
        secure=False,  # Set to True when served over HTTPS
    )

    logger.info(f"User '{result.username}' logged in (role={result.role!r})")
    return {"ok": True, "username": result.username, "role": result.role}


@router.post("/logout")
async def logout(response: Response) -> dict:
    """Clear the JWT cookie."""
    response.delete_cookie(key=_COOKIE_NAME, samesite="lax")
    return {"ok": True}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest) -> dict:
    """
    Create a new user account.

    The very first user to register is automatically granted admin privileges.
    Subsequent registrations create regular users.

    Only available when AUTH_ENABLED=true.
    """
    if not AUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Auth is disabled — registration is not available.",
        )

    # Check whether this will be the first (admin) user before writing
    first = is_first_user()

    # Prevent duplicate usernames
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
