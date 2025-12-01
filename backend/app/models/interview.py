from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Input schema when creating/saving an interview
class InterviewCreate(BaseModel):
    questions: List[str]
    answers: List[str]
    role: Optional[str] = None
    level: Optional[str] = None
    type: Optional[str] = None
    techstack: Optional[List[str]] = None
    # Evaluation fields
    evaluations: List[dict] = []   # Per-question scores
    overall_score: Optional[float] = None
    feedback: Optional[str] = None
    strengths: List[str] = []
    weaknesses: List[str] = []


# Schema for MongoDB document
class InterviewInDB(InterviewCreate):
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Response schema
class InterviewResponse(InterviewInDB):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True
        orm_mode = True
