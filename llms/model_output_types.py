from pydantic import BaseModel
from typing import List

class Event(BaseModel):
    timestamp_label: str
    data_or_summary: str

class Session(BaseModel):
    events: List[Event]

class ToolSession(BaseModel):
    tool_name: str
    session: Session

class SummarizedSessions(BaseModel):
    sessions: List[ToolSession]