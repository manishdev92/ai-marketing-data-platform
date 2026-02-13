from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class Message(BaseModel):
    role: str = Field(..., example="user")
    content: str

class ConversationCreate(BaseModel):
    user_id: str
    session_id: str
    messages: List[Message]
    timestamp: datetime
