from pydantic import BaseModel, validator
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import json

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