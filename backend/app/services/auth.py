import bcrypt
import jwt
import datetime
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models import User

security = HTTPBearer()

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a cleartext password using bcrypt."""
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a cleartext password against a hashed bcrypt password."""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
        """Create a JWT access token containing the payload data."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.utcnow() + expires_delta
        else:
            expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """Decode a JWT access token, verifying its validity and expiration."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except (jwt.PyJWTError, Exception):
            return None

    @staticmethod
    def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security), 
        db: Session = Depends(get_db)
    ) -> User:
        """Dependency for retrieving the authenticated user from a bearer token."""
        token = credentials.credentials
        payload = AuthService.decode_access_token(token)
        if not payload or "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        username = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user

