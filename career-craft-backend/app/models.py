from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    resumes = relationship("Resume", back_populates="owner", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String, nullable=False, default="Untitled Resume")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="resumes")
    
    __table_args__ = (
        Index('idx_user_id_created', user_id, created_at),
    )