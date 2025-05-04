"""
Pydantic models for request and response validation.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class QuestionRequest(BaseModel):
    """Request model for asking a question."""
    question: str = Field(..., description="The question to ask about the document")
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What are the main requirements for insurance coverage?"
            }
        }

class AnswerResponse(BaseModel):
    """Response model for answering a question."""
    answer: str = Field(..., description="The answer to the question")
    
    class Config:
        schema_extra = {
            "example": {
                "answer": "The main requirements for insurance coverage include..."
            }
        }

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="The status of the application")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "ok"
            }
        }

class Token(BaseModel):
    """Model for access tokens."""
    token: str = Field(..., description="Unique access token")
    customer_name: str = Field(..., description="Customer name")
    email: str = Field(..., description="Customer email")
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="active", description="Token status (active or revoked)")

class TokenResponse(BaseModel):
    """Response model for token generation."""
    token: str = Field(..., description="Generated access token")
    url: str = Field(..., description="Full access URL with token")

class UserInteraction(BaseModel):
    """Model for a single user interaction."""
    timestamp: datetime
    question: str
    answer: str


class UserStats(BaseModel):
    """Model for user interaction statistics."""
    token: str
    interaction_count: int
    last_activity: Optional[datetime]
    customer_name: Optional[str] = None  # Add this field
    email: Optional[str] = None          # Add this field

class InteractionStatsResponse(BaseModel):
    """Response model for interaction statistics."""
    total_users: int
    total_interactions: int
    users: List[UserStats]