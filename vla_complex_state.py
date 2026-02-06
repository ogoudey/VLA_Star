from typing import List, Optional, Any
from dataclasses import dataclass

@dataclass
class State:
    session: Optional[List[dict[str, str]]]=None    # of f"{timestamp()} Name:
    impression: Optional[Any] = None

    def add_to_session(self, session_event: dict[str, str]):
        self.session.append(session_event)