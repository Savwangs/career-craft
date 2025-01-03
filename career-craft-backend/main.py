from fastapi import FastAPI, HTTPException, Depends, Header, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import Base, engine, get_db
from app.models import User, Resume
from app.schemas import (
    UserBase, UserLogin, UserCreate, ResumeBase, ResumeCreate, 
    ResumeResponse, Token, PaginatedResponse
)
from app.utils import create_access_token, get_current_user
from app.exceptions import DatabaseError
from sqlalchemy.orm import Session
from firebase_admin import auth
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize database
Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="CareerCraft API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(DatabaseError)
async def database_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Database error occurred", "details": str(exc)},
    )

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to CareerCraft API"}

@app.post("/auth/register", response_model=Token)
@limiter.limit("5/minute")
async def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
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
        
        # Create user in database
        db_user = User(id=user_record.uid, email=user.email)
        db.add(db_user)
        db.commit()
        
        # Create access token
        access_token = create_access_token({"sub": user.email})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_record.uid
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Log in a user by verifying their email and password.
    """
    try:
        # Get Firebase authentication configuration
        api_key = os.getenv("FIREBASE_API_KEY")
        
        # Create the sign-in request URL
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        
        # Prepare the request payload
        payload = {
            "email": user.email,
            "password": user.password,
            "returnSecureToken": True
        }
        
        # Make the authentication request
        response = requests.post(auth_url, json=payload)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Invalid email or password"
            )
            
        firebase_user = auth.get_user_by_email(user.email)
        
        # Generate access token
        access_token = create_access_token({"sub": user.email})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=firebase_user.uid
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid email or password")

@app.post("/resumes/", response_model=ResumeResponse)
@limiter.limit("5/minute")
async def create_resume(
    request: Request,
    resume: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        firebase_user = auth.get_user_by_email(current_user)
        
        db_resume = Resume(
            content=resume.content,
            title=resume.title,
            user_id=firebase_user.uid
        )
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        return db_resume
    except Exception as e:
        db.rollback()
        raise DatabaseError(str(e))

@app.get("/resumes/", response_model=PaginatedResponse)
async def list_resumes(
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        firebase_user = auth.get_user_by_email(current_user)
        skip = (page - 1) * size
        
        total = db.query(Resume)\
            .filter(Resume.user_id == firebase_user.uid)\
            .count()
            
        resumes = db.query(Resume)\
            .filter(Resume.user_id == firebase_user.uid)\
            .order_by(Resume.created_at.desc())\
            .offset(skip)\
            .limit(size)\
            .all()
            
        return {
            "items": resumes,
            "total": total,
            "page": page,
            "size": size
        }
    except Exception as e:
        raise DatabaseError(str(e))

@app.get("/resumes/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        firebase_user = auth.get_user_by_email(current_user)
        resume = db.query(Resume)\
            .filter(Resume.id == resume_id, Resume.user_id == firebase_user.uid)\
            .first()
        if resume is None:
            raise HTTPException(status_code=404, detail="Resume not found")
        return resume
    except HTTPException:
        raise
    except Exception as e:
        raise DatabaseError(str(e))

@app.put("/resumes/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: int,
    resume: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        firebase_user = auth.get_user_by_email(current_user)
        db_resume = db.query(Resume)\
            .filter(Resume.id == resume_id, Resume.user_id == firebase_user.uid)\
            .first()
        if db_resume is None:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        db_resume.content = resume.content
        db_resume.title = resume.title
        db_resume.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_resume)
        return db_resume
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(str(e))

@app.delete("/resumes/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        firebase_user = auth.get_user_by_email(current_user)
        db_resume = db.query(Resume)\
            .filter(Resume.id == resume_id, Resume.user_id == firebase_user.uid)\
            .first()
        if db_resume is None:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        db.delete(db_resume)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)