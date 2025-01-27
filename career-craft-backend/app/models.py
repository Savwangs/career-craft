from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    firebase_uid = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    resumes = relationship("Resume", back_populates="user")

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    summary = Column(Text)
    contact_info = Column(JSON)  # Store phone, address, etc.
    target_job_description = Column(Text)
    original_resume_url = Column(String, nullable=True)  # For uploaded resumes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resume_type = Column(String, default="My Resume")
    
    user = relationship("User", back_populates="resumes")
    education = relationship("Education", back_populates="resume")
    experience = relationship("Experience", back_populates="resume")
    skills = relationship("Skill", back_populates="resume")
    projects = relationship("Project", back_populates="resume")
    achievements = relationship("Achievement", back_populates="resume")

class Education(Base):
    __tablename__ = "education"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    institution = Column(String)
    degree = Column(String)
    field_of_study = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    gpa = Column(String, nullable=True)
    
    resume = relationship("Resume", back_populates="education")

class Experience(Base):
    __tablename__ = "experience"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    company = Column(String)
    position = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    description = Column(Text)
    highlights = Column(JSON)  # Array of achievement bullets
    
    resume = relationship("Resume", back_populates="experience")

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    name = Column(String)
    category = Column(String)  # e.g., Technical, Soft Skills, Languages
    proficiency_level = Column(String, nullable=True)
    
    resume = relationship("Resume", back_populates="skills")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    title = Column(String)
    description = Column(Text)
    technologies = Column(JSON)  # Array of technologies used
    url = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    resume = relationship("Resume", back_populates="projects")

class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    title = Column(String)
    description = Column(Text)
    date = Column(DateTime, nullable=True)
    
    resume = relationship("Resume", back_populates="achievements")