from datetime import datetime
from typing import List, Dict, Any
import json

TIMESTAMP_FORMAT = "[%Y-%m-%d %H:%M:%S]"

from vla_complex_state import State

class Context:
    sessions: dict[str, List]
    impressions: dict[str, Any]

    def __repr__(self):
        return json.dumps({
            "Sessions": self.sessions,
            "Impressions": self.impressions,
        })

    def __init__(self, vla_complexes):
        self.pull_states(vla_complexes)

    def pull_states(self, vla_complexes):
        self.sessions = {}
        self.impressions = {}
        for vla_complex in vla_complexes:
            state: State = vla_complex.pull_state
            if state.session:
                self.sessions[vla_complex.name_in_session] = state.session
            if state.impression:
                self.impressions[vla_complex.name_in_impression] = state.impression

            
        


class OrderedContext:
    session: List
    impressions: dict[str, Any]

    def __repr__(self):
        return json.dumps({
            "Session": self.session,
            "Impressions": self.impressions
        })

    def order(self, context):
        self.session = [] # Ordered session
        self.session = self.order_in_time(context.sessions)

        self.impressions = context.impressions
        pass

    def __init__(self, context: Context):
        self.order(context)

    def order_in_time(self, *lists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Orders elements from multiple lists based on the timestamp
        embedded in their dictionary keys.
        """

        def extract_timestamp(item: Dict[str, Any]) -> datetime:
            key = next(iter(item.keys()))
            timestamp_str = key.split("]")[0] + "]"
            return datetime.strptime(timestamp_str, TIMESTAMP_FORMAT)

        combined = [item for lst in lists for item in lst]
        return sorted(combined, key=extract_timestamp)