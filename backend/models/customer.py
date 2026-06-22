from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class LeadStatus(str, Enum):
    PENDING = "PENDING"
    CALL_INITIATED = "CALL_INITIATED"
    QUALIFIED = "QUALIFIED"
    NOT_INTERESTED = "NOT_INTERESTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    FAILED = "FAILED"


class Customer(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    company_id: str
    name: str
    phone_number: str
    status: LeadStatus = LeadStatus.PENDING
    call_id: Optional[str] = None
    llm_confidence: Optional[float] = None
    last_called_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    status: Optional[LeadStatus] = None
    call_id: Optional[str] = None
    llm_confidence: Optional[float] = None
    last_called_at: Optional[datetime] = None
