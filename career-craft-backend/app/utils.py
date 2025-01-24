from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, exceptions as firebase_exceptions
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from .database import get_db
from . import models
import os

# Get secrets from environment variables
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

security = HTTPBearer()

def create_access_token(data: dict):
    """Create a new access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Validate Firebase token and get current user."""
    try:
        token = credentials.credentials
        # Verify the Firebase token
        try:
            decoded_token = auth.verify_id_token(token)
        except firebase_exceptions.InvalidIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        except firebase_exceptions.FirebaseError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Firebase authentication failed: {str(e)}"
            )
        
        # Get user from database
        user = db.query(models.User).filter(
            models.User.firebase_uid == decoded_token['uid']
        ).first()
        
        if not user:
            # Create user if they don't exist in the database
            try:
                firebase_user = auth.get_user(decoded_token['uid'])
                user = models.User(
                    email=firebase_user.email,
                    firebase_uid=firebase_user.uid
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create user: {str(e)}"
                )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )

def verify_firebase_token(token: str) -> dict:
    """Verify Firebase token and return decoded token."""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except firebase_exceptions.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except firebase_exceptions.FirebaseError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firebase authentication failed: {str(e)}"
        )