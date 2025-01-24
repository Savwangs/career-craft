from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    firebase_uid: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class EducationBase(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    start_date: Optional[datetime] = None  # Make optional
    end_date: Optional[datetime] = None
    gpa: Optional[str] = None

class Education(EducationBase):
    id: int

    class Config:
        from_attributes = True

class ExperienceBase(BaseModel):
    company: str
    position: str
    start_date: Optional[datetime] = None  # Make optional
    end_date: Optional[datetime] = None
    description: str = ""
    highlights: List[str] = []

class Experience(ExperienceBase):
    id: int

    class Config:
        from_attributes = True

class SkillBase(BaseModel):
    name: str
    category: str
    proficiency_level: Optional[str]

class Skill(SkillBase):
    id: int

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    title: str
    description: str
    technologies: List[str]
    url: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]

class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True

class AchievementBase(BaseModel):
    title: str
    description: str
    date: Optional[datetime]

class Achievement(AchievementBase):
    id: int

    class Config:
        from_attributes = True

class ResumeBase(BaseModel):
    title: str
    summary: str
    contact_info: Dict[str, str]
    target_job_description: Optional[str]

class ResumeCreate(ResumeBase):
    education: List[EducationBase]
    experience: List[ExperienceBase]
    skills: List[SkillBase]
    projects: Optional[List[ProjectBase]]
    achievements: Optional[List[AchievementBase]]
    target_job_description: str

class Resume(ResumeBase):
    id: int
    user_id: int
    original_resume_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    education: List[Education]
    experience: List[Experience]
    skills: List[Skill]
    projects: List[Project]
    achievements: List[Achievement]

    class Config:
        from_attributes = True

class JobRecommendation(BaseModel):
    title: str
    key_responsibilities: List[str]
    required_skills: List[str]
    category: str
    match_score: float

class ResumeFeedback(BaseModel):
    overall_score: float
    suggestions: List[str]
    missing_skills: List[str]
    improvement_areas: Dict[str, List[str]]
    job_recommendations: List[JobRecommendation]

class ResumeResponse(BaseModel):
    resume: Resume
    feedback: Optional[ResumeFeedback]
    
    class Config:
        from_attributes = True