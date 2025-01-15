from fastapi import FastAPI, HTTPException, Depends, Header, Request, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import Base, engine, get_db
from app.models import User, Resume
from app.schemas import (
    UserBase, UserLogin, UserCreate, ResumeBase, ResumeCreate, 
    ResumeResponse, Token, PaginatedResponse, ResumeGenerationRequest
)
from app.utils import create_access_token, get_current_user, convert_docx_to_pdf
from app.exceptions import DatabaseError
from app.resume_generator import ResumeGenerator
from sqlalchemy.orm import Session
from firebase_admin import auth
from app.utils import initialize_firebase_admin
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import tempfile
from pathlib import Path
from app.resume_parser import ResumeParser
from app.schemas import ParsedResume, ResumeUploadResponse
from app.resume_analyzer import ResumeAnalyzer
import logging
import base64

logging.basicConfig(level=logging.INFO)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


load_dotenv()

initialize_firebase_admin()

# Initialize analyzer
resume_analyzer = ResumeAnalyzer()

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
    allow_origins=[
        "http://localhost:3000",  # React development server
        os.getenv("FRONTEND_URL", "http://localhost:8000")
    ],
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

# In main.py, update the generate-resume endpoint
@app.post("/generate-resume")
async def generate_resume(
    request: Request,
    resume_data: ResumeGenerationRequest,
    current_user: str = Depends(get_current_user)
):
    try:
        logging.info("Starting resume generation process")
        
        if not resume_data.personal_info:
            raise HTTPException(status_code=400, detail="Missing personal information")
            
        generator = ResumeGenerator()
        doc, feedback = generator.generate(resume_data.dict())
        
        try:
            logging.info("Converting document to PDF")
            pdf_content, conversion_method = convert_docx_to_pdf(doc)
            
            if not pdf_content:
                raise ValueError("PDF conversion produced empty content")
                
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            
            return {
                "pdf": pdf_base64,
                "feedback": feedback,
                "conversion_method": conversion_method,
                "recommendations": []
            }
            
        except Exception as e:
            logging.error(f"PDF conversion error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"PDF conversion failed: {str(e)}. Please ensure LibreOffice is installed."
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Resume generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Resume generation failed: {str(e)}"
        )

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

@app.post("/upload-resume", response_model=ResumeUploadResponse)
@limiter.limit("5/minute")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    try:
        allowed_types = [
            "application/pdf",
            "application/docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="File must be PDF or DOCX format"
            )

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            parser = ResumeParser()
            parsed_data = parser.parse(temp_file_path, file.content_type)
            
            # Create feedback based on missing sections
            feedback = []
            if parsed_data.get("missing_sections"):
                for section in parsed_data["missing_sections"]:
                    feedback.append(f"Consider adding a {section.title()} section to strengthen your resume")
            
            Path(temp_file_path).unlink()
            
            return ResumeUploadResponse(
                message="Resume successfully parsed",
                parsed_data=ParsedResume(**parsed_data),
                feedback=feedback
            )
            
        except Exception as e:
            Path(temp_file_path).unlink()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse resume: {str(e)}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process resume: {str(e)}"
        )

@app.post("/analyze-resume")
async def analyze_resume(
    resume_id: int,
    job_description: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Get the resume from database
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Analyze resume
    try:
        analysis = resume_analyzer.analyze_resume(
            json.loads(resume.content),
            job_description
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/suggest-jobs/{resume_id}")
async def suggest_jobs(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Get the resume
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get job suggestions
    try:
        suggestions = resume_analyzer.suggest_job_titles(json.loads(resume.content))
        return {"job_titles": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)