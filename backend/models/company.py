from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Company(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    industry: str
    vapi_assistant_id: str = ""
    system_prompt: str
    created_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class CompanyCreate(BaseModel):
    name: str
    industry: str
    vapi_assistant_id: str = ""
    system_prompt: str
