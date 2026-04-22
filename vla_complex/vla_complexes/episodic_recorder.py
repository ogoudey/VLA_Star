import threading

from ..vla_complex import VLA_Complex
from vla_complex_state import State

class EpisodicRecorder(VLA_Complex):
    """
j
    """
    def __init__(self, interaction_runner, tool_name):
        self.interaction_runner = interaction_runner
        super().__init__(None, tool_name,True)
        self.running = False
        self.conducting = False
        # instantiates signal to coordinate monitors with runner (both are in the runner)
        self.signal:dict={"RUNNING_LOOP":False, "RUNNING_E": True, "task":"Put the cube in the first aid kit"}
        if interaction_runner.demoed:
            self.signal["DECISION"] = None
        # signal at first blocks episode loop, waiting for "go" from teleop
        self.state = State(session=[])

    async def execute(self, instruction: str):
        """
        does a thing
        :param instruction: task to do
        """
        await super().execute(instruction)
        self.signal["task"] = instruction
        self.signal["RUNNING_LOOP"] = True
        print(f"Changed signal to {self.signal}")
        if not self.running:
            threading.Thread(target=self.interaction_runner.run, args=(self.signal,), daemon=True).start()
            self.running = True
        print("Success. Return immediately.")