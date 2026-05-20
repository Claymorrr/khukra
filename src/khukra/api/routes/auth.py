from fastapi import APIRouter, Depends, HTTPException, status

from khukra.api.schemas import LoginRequest, RegisterRequest, TokenResponse
from khukra.auth.deps import get_current_user, require_user
from khukra.auth.security import create_access_token, hash_password, verify_password
from khukra.data.repositories.users import UserRepository

router = APIRouter(prefix="/auth")
users_repo = UserRepository()


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest) -> TokenResponse:
    user = users_repo.get_by_email(body.email)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    token = create_access_token(user["user_id"], user["email"], user["role"])
    return TokenResponse(
        access_token=token,
        user={
            "user_id": user["user_id"],
            "email": user["email"],
            "display_name": user["display_name"],
            "role": user["role"],
        },
    )


@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest) -> TokenResponse:
    if users_repo.get_by_email(body.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    user_id = users_repo.create(
        email=body.email,
        display_name=body.display_name,
        password_hash=hash_password(body.password),
    )
    user = users_repo.get_by_id(user_id)
    token = create_access_token(user["user_id"], user["email"], user["role"])
    return TokenResponse(
        access_token=token,
        user={
            "user_id": user["user_id"],
            "email": user["email"],
            "display_name": user["display_name"],
            "role": user["role"],
        },
    )


@router.get("/me")
def me(user: dict = Depends(require_user)) -> dict:
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "display_name": user["display_name"],
        "role": user["role"],
    }


@router.get("/optional-me")
def optional_me(user: dict | None = Depends(get_current_user)) -> dict:
    if not user:
        return {"authenticated": False}
    return {"authenticated": True, **user}
