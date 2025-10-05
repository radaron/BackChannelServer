from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.security import authenticate_user, create_access_token
from app.schemas.user import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, response: Response) -> LoginResponse:
    """Login with master password using LoginManager"""
    user = authenticate_user(login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )

    # Create access token using LoginManager
    access_token = create_access_token(user.username)

    # Set the token as a cookie
    response.set_cookie(
        key=settings.cookie_name,
        value=access_token,
        max_age=settings.session_expire_minutes * 60,
        path="/",
        secure=False,  # Set to True in production with HTTPS
        httponly=True,
        samesite="lax",
    )

    return LoginResponse(message="Successfully logged in", authenticated=True)


@router.post("/logout")
def logout(response: Response) -> JSONResponse:
    """Logout and clear cookie"""
    response.delete_cookie(key=settings.cookie_name, path="/")
    return JSONResponse({"message": "Successfully logged out"})
