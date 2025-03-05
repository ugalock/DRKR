from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer, APIKeyHeader
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import json
import httpx
from functools import lru_cache
from authlib.jose import JsonWebEncryption

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

credentials_exception = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# Create an instance of the JWE handler
jwe = JsonWebEncryption()

# Fetch and cache JWKS (JSON Web Key Set) from Auth0
@lru_cache(maxsize=1)
def get_jwks():
    url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()

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

async def verify_jwt_token(token: str, audience: str = None):
    """
    Verify a JWT token using RS256. Since RS256 uses a public key, we need to fetch a public key from a JWKS endpoint.
    """
    try:
        # Get the key ID (kid) from the token header
        unverified_header = jwt.get_unverified_header(token)
        if unverified_header.get("alg") == "dir":
            # The `deserialize_compact` method decrypts the JWE token.
            # It returns a dictionary with keys: 'header', 'payload', etc.
            decrypted = jwe.deserialize_compact(token, bytes.fromhex(settings.AUTH0_CLIENT_SECRET))
            
            # Get the decrypted payload. It is the inner JWT as bytes.
            decrypted_payload = decrypted.get("payload")
            
            # If payload is bytes, decode it to a string.
            if isinstance(decrypted_payload, bytes):
                decrypted_payload = decrypted_payload.decode("utf-8")    

            token = decrypted_payload
            unverified_header = jwt.get_unverified_header(token)
        
        kid = unverified_header.get("kid")
        if kid is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Fetch JWKS
        jwks = get_jwks()
        # Find the matching key in JWKS
        rsa_key = next(key for key in jwks["keys"] if key["kid"] == kid)
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=[settings.JWT_ALGORITHM],
            audience=audience or f"{settings.API_SCHEME}://{settings.API_HOST}{':' if settings.API_PORT else ''}{settings.API_PORT}",
            # audience=settings.AUTH0_CLIENT_ID,
            issuer=f"https://{settings.AUTH0_DOMAIN}/"
        )
        return payload
    except jwt.ExpiredSignatureError:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except JWTError:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    
    return payload

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current user from a JWT token"""
    
    try:
        payload = await verify_jwt_token(token)
        sub: str = payload.get("sub")
        auth_provider, external_id = sub.split("|")
    except HTTPException:
        raise
    except:
        raise credentials_exception
    if external_id is None:
        raise credentials_exception
        
    query = select(User).where(User.external_id == external_id).options(selectinload(User.organization_memberships))
    user = await db.execute(query)
    user = user.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

async def create_user_if_not_exists(
    id_token: str,
    db: AsyncSession = Depends(get_db)
) -> User:
    """Create a user if they don't exist, and return the user object"""
    
    try:
        payload = await verify_jwt_token(id_token, audience=settings.AUTH0_CLIENT_ID)
        sub: str = payload.get("sub")
        auth_provider, external_id = sub.split("|")
    except HTTPException:
        import traceback
        traceback.print_exc()
        raise
    except:
        import traceback
        traceback.print_exc()
        raise credentials_exception
    if external_id is None:
        raise credentials_exception
    
    query = select(User).where(User.external_id == external_id)
    user = await db.execute(query)
    user = user.scalar_one_or_none()
    if user is None:
        display_name = payload.get("name") or payload.get("email").split("@")[0]
        user = User(
            external_id=external_id,
            auth_provider=auth_provider,
            email=payload.get("email"),
            display_name=display_name,
            username=display_name,
            picture_url=payload.get("picture"),
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return user

async def verify_api_key(
    api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Verify an API key and return the associated user"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required")
        
    query = select(ApiKey).where(
        ApiKey.key == api_key,
        ApiKey.is_active == True,
        ApiKey.expires_at > datetime.utcnow()
    )
    db_api_key = await db.execute(query)
    db_api_key = db_api_key.scalar_one_or_none()
    
    if not db_api_key:
        raise HTTPException(status_code=401, detail="Invalid or expired API key")
        
    return db_api_key.user

