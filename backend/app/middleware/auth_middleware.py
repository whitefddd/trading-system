from fastapi import Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..services.auth_service import AuthService
from ..utils.logger import setup_logger

logger = setup_logger("auth_middleware")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def auth_middleware(request: Request, call_next):
    if request.url.path in ["/api/token", "/api/register"]:
        return await call_next(request)
        
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token = auth_header.split(" ")[1]
        username = AuthService.verify_token(token)
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        request.state.username = username
        return await call_next(request)
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise 