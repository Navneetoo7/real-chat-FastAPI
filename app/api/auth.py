from fastapi import APIRouter, Depends

from app.dependencies import get_user_repo
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, SignUpRequest, TokenResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(repo: UserRepository = Depends(get_user_repo)) -> AuthService:
    return AuthService(repo)


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(
    body: SignUpRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await service.signup(body)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await service.login(body)