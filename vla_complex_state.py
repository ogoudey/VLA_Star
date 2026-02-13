from typing import List, Optional, Any
from dataclasses import dataclass
from displays import log, timestamp, update_activity
import json
from pydantic import BaseModel






class State(BaseModel):
    session: Optional[list[dict[str, str]]] = None
    impression: Optional[Any] = None

    def add_to_session(self, event_label: str, event_data: str):
        session_event = {f"{timestamp()} {event_label}": event_data}
        self.session.append(session_event)

    @staticmethod
    def form_map_from_vlac_name_to_vlac_state(vlacs) -> dict[str, "State"]:
        d = dict()
        for vlac in vlacs:
            d[vlac.tool_name] = vlac.state
        return d
    
    @staticmethod
    def states_to_json(obj: dict[str, "State"]) -> str:
        return json.dumps(
            {k: v.model_dump(mode="json") for k, v in obj.items()}
        )
