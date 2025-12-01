from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Education entry
class Education(BaseModel):
    institution: str
    degree: str
    field: str
    graduation_year: Optional[int] = None


# Work experience entry
class Experience(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: Optional[str] = None  # None means current job
    bullets: List[str] = []


# Project entry
class Project(BaseModel):
    name: str
    description: str
    tech_stack: List[str] = []


# Skills grouped by category
class Skills(BaseModel):
    hard_skills: List[str] = []
    soft_skills: List[str] = []
    languages: List[str] = []


# Input schema when creating/updating profile
class UserProfileCreate(BaseModel):
    cv_text: Optional[str] = None
    headline: Optional[str] = None
    education: List[Education] = []
    experience: List[Experience] = []
    projects: List[Project] = []
    skills: Optional[Skills] = None


# Schema for MongoDB document
class UserProfileInDB(UserProfileCreate):
    user_id: str
    strengths: List[str] = []  # From interview performance
    weaknesses: List[str] = []  # From interview performance
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Response schema
class UserProfileResponse(UserProfileInDB):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True
        orm_mode = True
