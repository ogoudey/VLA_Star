from typing import List, Optional, Any
from dataclasses import dataclass
from displays import log, timestamp, update_activity

from pydantic import BaseModel






class State(BaseModel):
    session: Optional[list[dict[str, str]]] = None
    impression: Optional[Any] = None

    def add_to_session(self, event_label: str, event_data: str):
        session_event = {f"{timestamp()} {event_label}": event_data}
        self.session.append(session_event)
