from vla_complex_state import State
from typing import List
import json
from agents import Agent, Runner, RunConfig
from pydantic import BaseModel

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

class Summarizer:
    def __init__(self):
        self.identities_cnt = 0
        self.model = "o4-mini"
        self.identity = None

    async def compress_all_states(self, vla_complexes) -> dict[str, State]:
        states: dict[str, State] = State.form_map_from_vlac_name_to_vlac_state(vla_complexes)
        edible = State.states_to_json(states)
        self.create_identity()
        return await self.run_identity(edible)


    def update_vla_complexes(self, vla_complexes, states: SummarizedSessions):
        session_by_tool = {
            tool_session.tool_name: tool_session.session
            for tool_session in states.sessions
        }

        for vla_complex in vla_complexes:
            session = session_by_tool.get(vla_complex.tool_name)
            if session is not None:
                #Session(events=[Event(timestamp_label='[2026-02-07 14:19:42]', data_or_summary='picked up breakfast')])
                vla_complex.state.session = []
                for event in session.events:
                    rephrased = {event.timestamp_label: event.data_or_summary}
                    vla_complex.state.session.append(rephrased)

    
    
    def create_identity(self):
        self.identities_cnt += 1
        self.identity = Agent(
            name=f"summarizer{self.identities_cnt}",
            instructions=self.instance_system_prompt(),
            model=self.model,
            output_type=SummarizedSessions
        )

    async def run_identity(self, prompt):
        result = await Runner.run(self.identity, prompt)
        print(f"End summarizing.")
        return result.final_output
    
    def instance_system_prompt(self):
        instructions1 = """
You are responsible for executing a precise and important task. Given highly structured, real-world, data, edit the contents such that the data is more readable, while still precisely representing the data.
Do not make up any information that is not present in the data.

If a session is <2 items in length, you may leave it as such.

Pay close attention to the in-the-moment direction, motivation, and state of the context.

Be perfectly rational and attentive to the timing of things. The events in the context/data represent actual goings-on in the real, physical world.

If data is already readable, it's because its already summarized. Since the data moves through time, you should COMPRESS the information among events.

All data must have a timestamp of the form f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]" or [%Y-%m-%d %H:%M:%S], e.g. [2026-02-07 11:41:54]. For periods of time, of course pick a single reasonable moment. This all must be intuitively understandable. No ranges, just 

Above all, output form must match the requested output type, a SummarizedSessions pydantic object.
"""
        return instructions1