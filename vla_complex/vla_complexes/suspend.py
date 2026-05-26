from ..vla_complex import VLA_Complex


class Suspend(VLA_Complex):

    def __init__(self, tool_name, description, return_value, on_start, monitors, recorded):
        super().__init__(tool_name, description, return_value, on_start, monitors, recorded)

    async def execute(self):
        self.deactivate_self()

    def deactivate_self(self):
        raise KeyboardInterrupt("Suspending from Suspend VLA_Complex")