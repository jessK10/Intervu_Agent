from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# Job requirements extracted from JD
class JobRequirements(BaseModel):
    hard_skills: List[str] = []
    soft_skills: List[str] = []
    responsibilities: List[str] = []
    must_have: List[str] = []
    nice_to_have: List[str] = []


# Tailored resume sections
class TailoredResume(BaseModel):
    summary: str
    experience: List[Dict[str, Any]] = []  # Rewritten experience bullets
    projects: List[Dict[str, Any]] = []     # Selected projects
    skills: List[str] = []                   # Matched skills


# Application messages
class ApplicationMessages(BaseModel):
    email_subject: str
    email_body: str
    linkedin_note: str
    linkedin_followup: str


# Input schema when creating application
class ApplicationCreate(BaseModel):
    job_title: str
    company: str
    job_url: Optional[str] = None
    job_description: str
    job_requirements: JobRequirements
    tailored_resume: Optional[TailoredResume] = None
    motivation_letter: Optional[str] = None
    messages: Optional[ApplicationMessages] = None


# Schema for MongoDB document
class ApplicationInDB(ApplicationCreate):
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Response schema
class ApplicationResponse(ApplicationInDB):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True
        orm_mode = True
