from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return ObjectId(v) if not isinstance(v, ObjectId) else v

class UserInDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str  # ✅ added name so it matches frontend + schemas
    email: EmailStr
    hashed_password: str  # ✅ renamed to match security + auth
    role: str = "candidate"  # ✅ keep this as default

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
