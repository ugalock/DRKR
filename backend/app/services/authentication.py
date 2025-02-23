from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer, APIKeyHeader
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User, ApiKey
from app.config import settings

# OAuth2 configuration
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{settings.AUTH0_DOMAIN}/authorize",
    tokenUrl=f"https://{settings.AUTH0_DOMAIN}/oath/token"
)

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def create_jwt_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token with claims and expiration"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def verify_jwt_token(token: str = Depends(oauth2_scheme)):
    """
    Verify a JWT token using HS256. Since HS256 uses a shared secret, we don't
    need to fetch a public key from a JWKS endpoint. The token is decoded with
    the shared secret (e.g. settings.AUTH0_CLIENT_SECRET).
    """
    try:
        payload = jwt.decode(
            token,
            settings.AUTH0_CLIENT_SECRET,  # Shared secret for HS256 signing
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.AUTH0_AUDIENCE,
            issuer=f"https://{settings.AUTH0_DOMAIN}/"
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return payload

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current user from a JWT token"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = await verify_jwt_token(token)
        user_id: str = payload.get("sub")
    except HTTPException:
        raise
    except:
        raise credentials_exception
    if user_id is None:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

async def verify_api_key(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    """Verify an API key and return the associated user"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required")
        
    db_api_key = db.query(ApiKey).filter(
        ApiKey.key == api_key,
        ApiKey.is_active == True,
        ApiKey.expires_at > datetime.utcnow()
    ).first()
    
    if not db_api_key:
        raise HTTPException(status_code=401, detail="Invalid or expired API key")
        
    return db_api_key.user

