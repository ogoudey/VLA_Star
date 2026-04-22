import threading

from ..vla_complex import VLA_Complex
from vla_complex_state import State

class VLA_Tester(VLA_Complex):
    def __init__(self, interaction_runner, tool_name):
        print("Initializing VLA_Tester")
        self.interaction_runner = interaction_runner
        super().__init__(None, tool_name)
        self.running = False

        # instantiates signal to coordinate monitors with runner (both are in the runner)
        self.signal:dict={"RUNNING_LOOP":True, "RUNNING_E": True, "task":"Stack the blocks"}
        # signal at first blocks episode loop, waiting for "go" from teleop
        self.state = State(session=[])

    async def execute(self, instruction: str):
        """
        does a thing
        :param instruction: task to do
        """
        await super().execute(instruction)
        if not self.running:
            threading.Thread(target=self.interaction_runner.run, args=(self.signal,), daemon=True).start()
        if instruction == "STOP":
            self.signal["RUNNING_E"] = False
        else:
            self.signal["RUNNING_LOOP"] = True
            self.signal["RUNNING_E"] = True
            self.signal["task"] = instruction
        print("Action applied. Return immediately.")