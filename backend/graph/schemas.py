from typing import TypedDict, List, Optional, Dict
from pydantic import BaseModel, Field


class EmailSchema(BaseModel):
    """Schema for email"""
    recipient: str = Field(..., description="To email address")
    subject: str = Field(..., description="Subject of the email")
    body: str = Field(..., description="Body of the email")
    
class LinkedInMessageSchema(BaseModel):
    """Schema for LinkedIn message"""
    recipient: str = Field(..., description="To LinkedIn profile ")
    subject: str = Field(..., description="Subject of the message")
    body: str = Field(..., description="Body of the message")

class CoverLetterSchema(BaseModel):
    """Schema for cover letter"""
    body: str = Field(..., description="Body of the cover letter")