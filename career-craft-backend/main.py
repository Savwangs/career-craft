from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import tempfile
import os
import firebase_admin
from firebase_admin import credentials, auth
from datetime import datetime

from app.database import get_db, engine
from app.models import Base  # Add this import
from app import models  # Add this import
from app.schemas import (
    UserCreate, User, Resume, ResumeCreate, ResumeFeedback,
    JobRecommendation
)
from app.resume_parser import ResumeParser
from app.resume_generator import ResumeGenerator
from app.resume_analyzer import ResumeAnalyzer
from app.utils import get_current_user

# Initialize Firebase Admin - Update the path to your service account key
# Initialize Firebase Admin
cred = credentials.Certificate(os.getenv('FIREBASE_ADMIN_SDK_PATH'))
firebase_admin.initialize_app(cred, {
    'projectId': os.getenv('FIREBASE_PROJECT_ID')
})

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Career Craft API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
resume_parser = ResumeParser()
resume_generator = ResumeGenerator()
resume_analyzer = ResumeAnalyzer()

@app.post("/api/users", response_model=User)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    try:
        # Verify Firebase token
        auth.get_user(user.firebase_uid)
        
        # Create user in database
        db_user = models.User(
            email=user.email,
            firebase_uid=user.firebase_uid
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except auth.AuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token"
        )

@app.post("/api/resumes/upload", response_model=Resume)
async def upload_resume(
    file: UploadFile = File(...),
    job_description: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and parse a resume file."""
    if not job_description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is required"
        )

    allowed_types = {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx"
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are supported"
        )

    try:
        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)

        # Save uploaded file with correct extension
        file_extension = allowed_types[file.content_type]
        temp_path = f"temp/upload_{datetime.now().timestamp()}{file_extension}"

        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Parse resume
        resume_data = resume_parser.parse_resume(temp_path)

        # Create a new Resume object
        db_resume = models.Resume(
            user_id=current_user.id,
            title=resume_data.title or "Uploaded Resume",
            summary=resume_data.summary,
            contact_info=resume_data.contact_info,
            target_job_description=job_description,
            education=[
                models.Education(
                    institution=edu.institution,
                    degree=edu.degree,
                    field_of_study=edu.field_of_study,
                    start_date=edu.start_date,
                    end_date=edu.end_date,
                    gpa=edu.gpa
                ) for edu in resume_data.education or []
            ],
            experience=[
                models.Experience(
                    company=exp.company,
                    position=exp.position,
                    start_date=exp.start_date,
                    end_date=exp.end_date,
                    description=exp.description,
                    highlights=exp.highlights
                ) for exp in resume_data.experience or []
            ],
            skills=[
                models.Skill(
                    name=skill.name,
                    category=skill.category,
                    proficiency_level=skill.proficiency_level
                ) for skill in resume_data.skills or []
            ],
            projects=[
                models.Project(
                    title=proj.title,
                    description=proj.description,
                    technologies=proj.technologies or [],
                    url=proj.url,
                    start_date=proj.start_date,
                    end_date=proj.end_date
                ) for proj in resume_data.projects or []
            ],
            achievements=[
                models.Achievement(
                    title=ach.title,
                    description=ach.description,
                    date=ach.date
                ) for ach in resume_data.achievements or []
            ],
            resume_type="Parsed Resume",
            updated_at=datetime.now()
        )

        # Save to database
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)

        # Clean up temp file
        os.unlink(temp_path)

        return db_resume

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/resumes", response_model=Resume)
async def create_resume(
    resume: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new resume from form data."""
    if not resume.target_job_description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is required"
        )
    
    try:
        # Convert Pydantic model to dictionary and remove _sa_instance_state if present
        resume_dict = resume.dict()
        
        # Create database models for related entities
        db_education = [models.Education(**edu) for edu in resume_dict.pop('education', [])]
        db_experience = [models.Experience(**exp) for exp in resume_dict.pop('experience', [])]
        db_skills = [models.Skill(**skill) for skill in resume_dict.pop('skills', [])]
        db_projects = [models.Project(**proj) for proj in resume_dict.pop('projects', [])]
        db_achievements = [models.Achievement(**ach) for ach in resume_dict.pop('achievements', [])]
        
        # Create resume with user ID and other details
        db_resume = models.Resume(
            **resume_dict, 
            user_id=current_user.id, 
            resume_type="My Resume",
            updated_at=datetime.now(),
            education=db_education,
            experience=db_experience,
            skills=db_skills,
            projects=db_projects,
            achievements=db_achievements
        )
        
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        return db_resume
    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/resumes", response_model=List[Resume])
async def get_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all resumes for the current user."""
    return db.query(models.Resume).filter(models.Resume.user_id == current_user.id).all()

@app.get("/api/resumes/{resume_id}", response_model=Resume)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific resume by ID."""
    resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return resume

@app.put("/api/resumes/{resume_id}", response_model=Resume)
async def update_resume(
    resume_id: int,
    resume_update: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific resume."""
    db_resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.user_id == current_user.id
    ).first()
    
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Update resume fields
    for key, value in resume_update.dict().items():
        setattr(db_resume, key, value)
    
    db.commit()
    db.refresh(db_resume)
    return db_resume

@app.delete("/api/resumes/{resume_id}")
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific resume."""
    db_resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.user_id == current_user.id
    ).first()
    
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    db.delete(db_resume)
    db.commit()
    return {"message": "Resume deleted successfully"}

@app.post("/api/resumes/{resume_id}/analyze", response_model=ResumeFeedback)
async def analyze_resume(
    resume_id: int,
    job_description: str = Body(embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    feedback = resume_analyzer.analyze_resume(resume, job_description)
    return feedback

@app.post("/api/resumes/{resume_id}/generate")
async def generate_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a formatted resume document."""
    resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    try:
        # Generate resume document
        output_path = f"temp/resume_{resume_id}_{datetime.now().timestamp()}.docx"
        os.makedirs("temp", exist_ok=True)
        
        generated_path = resume_generator.generate(resume, output_path)
        
        # Return file
        return FileResponse(
            generated_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"resume_{resume_id}.docx"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/jobs/recommendations", response_model=List[JobRecommendation])
async def get_job_recommendations(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job recommendations based on a resume."""
    resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    recommendations = resume_analyzer._get_job_recommendations(
        resume,
        resume.target_job_description
    )
    return recommendations