from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from vla_complex import VLA_Complex
TIMESTAMP_FORMAT = "[%Y-%m-%d %H:%M:%S]"
from pydantic import BaseModel
from vla_complex_state import State
from vla_complex import VLA_Complex
from summarizer_compressor import Summarizer, SummarizedSessions
class Context:
    sessions: dict[str, List]
    impressions: dict[str, Any]

    def __str__(self):
        return json.dumps({
            "Sessions": self.sessions,
            "Impressions": self.impressions,
        }, indent=2)

    def __init__(self, vla_complexes:List[VLA_Complex]):
        
        self.pull_states(vla_complexes)

    def pull_states(self, vla_complexes):
        self.sessions = {}
        self.impressions = {}
        for vlac in vla_complexes:
            if vlac.state.session:
                self.sessions[vlac.tool_name] = vlac.state.session
            if vlac.state.impression:
                self.impressions[vlac.tool_name] = vlac.state.impression

class OrderedContext:
    session: List
    impressions: dict[str, Any]

    def __str__(self):
        return json.dumps({
            "Session": self.session,
            "Impressions": self.impressions
        }, indent=2)

    def order(self, context):
        self.session = self.order_sessions_in_time(context.sessions)
        self.impressions = context.impressions
        pass

    def __init__(self, context: Context):
        self.order(context)

    def order_sessions_in_time(
        self,
        sessions: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Orders all session entries across session types by timestamp
        embedded in their dictionary keys.
        """

        def extract_timestamp(item: Dict[str, Any]) -> datetime:
            key = next(iter(item.keys()))
            timestamp_str = key.split("]")[0] + "]"
            return datetime.strptime(timestamp_str, TIMESTAMP_FORMAT)

        # Flatten all session lists (arm, drive, etc.)
        combined = [
            session
            for session_list in sessions.values()
            for session in session_list
        ]

        return sorted(combined, key=extract_timestamp)