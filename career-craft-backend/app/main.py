from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth
from jose import jwt, JWTError
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK only if not already initialized
def initialize_firebase():
    try:
        return firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate("career-craft-98538-firebase-adminsdk-g7rtc-992c68a834.json")
        return firebase_admin.initialize_app(cred)

# Initialize Firebase
firebase_app = initialize_firebase()

# Constants from environment variables
SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("No JWT_SECRET environment variable set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Initialize FastAPI app
app = FastAPI(title="CareerCraft API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Authentication dependency
async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to CareerCraft API"}

@app.post("/auth/register", response_model=Token)
async def register(user: UserCreate):
    try:
        # Check if user exists
        try:
            existing_user = auth.get_user_by_email(user.email)
            raise HTTPException(status_code=400, detail="Email already registered")
        except auth.UserNotFoundError:
            pass
        
        # Create user in Firebase
        user_record = auth.create_user(
            email=user.email,
            password=user.password
        )
        
        # Create access token
        access_token = create_access_token({"sub": user.email})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_record.uid
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", response_model=Token)
async def login(user: UserCreate):
    try:
        # Verify user exists in Firebase
        firebase_user = auth.get_user_by_email(user.email)
        
        # Create access token
        access_token = create_access_token({"sub": user.email})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=firebase_user.uid
        )
    except auth.UserNotFoundError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/auth/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    try:
        user = auth.get_user_by_email(current_user)
        return {
            "email": user.email,
            "user_id": user.uid,
            "email_verified": user.email_verified
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)