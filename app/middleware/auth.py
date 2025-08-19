"""Authentication middleware for API key validation."""

from fastapi import Request, HTTPException, status
from app.config import settings
from app.util.logging import get_logger

logger = get_logger("auth")


async def verify_api_key(request: Request):
    """Verify API key from request headers."""
    
    # Skip authentication if not required
    if not settings.require_api_key or not settings.api_key:
        return True
    
    # Get API key from header
    api_key = request.headers.get(settings.api_key_header)
    
    if not api_key:
        logger.warning(f"Missing API key in header: {settings.api_key_header}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Missing API key. Please provide '{settings.api_key_header}' header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Verify API key
    if api_key != settings.api_key:
        logger.warning("Invalid API key provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    logger.debug("API key verified successfully")
    return True


def get_api_key_dependency():
    """Dependency for API key verification."""
    async def verify_api_key_dependency(request: Request):
        return await verify_api_key(request)
    return verify_api_key_dependency


