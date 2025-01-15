from pydantic import BaseModel, validator, EmailStr, Field
from typing import Optional, List
from datetime import datetime
import json
from fastapi import UploadFile
from enum import Enum
from typing import Dict, List, Any

# Existing schemas
class UserBase(BaseModel):
    email: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ResumeBase(BaseModel):
    title: Optional[str] = "Untitled Resume"
    content: str
    
    @validator('content')
    def validate_json_content(cls, v):
        try:
            json.loads(v)
            return v
        except json.JSONDecodeError:
            raise ValueError('Content must be valid JSON')

class ResumeCreate(ResumeBase):
    pass

class ResumeResponse(ResumeBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PaginatedResponse(BaseModel):
    items: List[ResumeResponse]
    total: int
    page: int
    size: int

# New schemas for resume generation
class Experience(BaseModel):
    title: str
    company: str
    start_date: str
    end_date: Optional[str]
    responsibilities: List[str]

class Education(BaseModel):
    degree: str
    field: str
    school: str
    graduation_date: str

class ResumeGenerationRequest(BaseModel):
    #personal_info: Dict[str, str]
    #summary: Optional[str] = None
    #experience: List[Dict[str, Any]]
    #education: List[Dict[str, Any]]
    #skills: List[str]
    #achievements: Optional[List[Dict[str, Any]]] = None
    personal_info: dict = Field(..., description="Personal information including name, email, phone, location")
    summary: str = Field(..., description="Professional summary")
    experience: List[dict] = Field(..., description="List of work experiences")
    education: List[dict] = Field(..., description="List of education entries")
    skills: List[str] = Field(..., description="List of skills")
    achievements: Optional[List[dict]] = Field(None, description="Optional list of achievements")

class ResumeSource(str, Enum):
    UPLOAD = "upload"
    MANUAL = "manual"

class ParsedResume(BaseModel):
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    summary: Optional[str]
    experience: Optional[List[Experience]]
    education: Optional[List[Education]]
    skills: Optional[List[str]]
    
    class Config:
        orm_mode = True

class ResumeUploadResponse(BaseModel):
    message: str
    parsed_data: ParsedResume
    feedback: List[str] = []

class KeywordAlignment(BaseModel):
    missing_keywords: List[str]
    suggestions: List[str]

class AchievementImprovement(BaseModel):
    section: str
    current: str
    suggested: str

class SkillsFeedback(BaseModel):
    relevant_skills: List[str]
    missing_skills: List[str]
    suggestions: List[str]

class ResumeAnalysis(BaseModel):
    keyword_alignment: KeywordAlignment
    achievement_improvements: List[AchievementImprovement]
    skills_feedback: SkillsFeedback
    overall_recommendations: List[str]

class Config:
        schema_extra = {
            "example": {
                "personal_info": {
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "phone": "123-456-7890",
                    "location": "New York, NY"
                },
                "summary": "Experienced software engineer...",
                "experience": [{
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "start_date": "2020-01",
                    "end_date": "2023-01",
                    "description": "Led development..."
                }],
                "education": [{
                    "institution": "University Name",
                    "degree": "Bachelor's in Computer Science",
                    "graduation_date": "2020-05",
                    "gpa": "3.8",
                    "relevant_courses": []
                }],
                "skills": ["Python", "JavaScript", "React"],
                "achievements": []
            }
        }