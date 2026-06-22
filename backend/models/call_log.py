from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TranscriptMessage(BaseModel):
    role: str  # "assistant" or "user"
    content: str
    time: Optional[float] = None


class CallLog(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    customer_id: str
    company_id: str
    call_id: str
    transcript: Optional[str] = None
    transcript_messages: Optional[List[TranscriptMessage]] = []
    summary: Optional[str] = None
    llm_reasoning: Optional[str] = None
    llm_confidence: Optional[float] = None
    key_signals: Optional[List[str]] = []
    outcome: Optional[str] = None
    duration_seconds: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
