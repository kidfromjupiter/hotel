from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_auth_service, get_current_user
from app.schemas.auth import LoginRequest, TokenResponse, StaffUser
from app.services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/login", response_model=TokenResponse)
def login(
    req: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Authenticate a staff member (Admin or Receptionist) and return a JWT access token.
    """
    user = auth_service.authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Payload stored inside the JWT token
    token_data = {
        "sub": str(user["staff_id"]),
        "staff_id": user["staff_id"],
        "username": user["username"],
        "role": user["role"],
        "branch_id": user.get("branch_id"),
    }
    access_token = auth_service.create_access_token(data=token_data)

    user_data = StaffUser(
        staff_id=user["staff_id"],
        branch_id=user.get("branch_id"),
        username=user["username"],
        full_name=user["full_name"],
        role=user["role"],
        is_active=user["is_active"],
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_data,
    )

@auth_router.get("/me", response_model=StaffUser)
def get_current_staff_profile(
    current_user: StaffUser = Depends(get_current_user),
):
    """
    Returns profile information of the currently logged-in user.
    Requires Bearer token.
    """
    return current_user

