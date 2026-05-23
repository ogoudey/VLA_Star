from ..vla_complex import VLA_Complex


class Suspend(VLA_Complex):

    def __init__(self, tool_name="suspend"):
        super().__init__(self.deactivate_self, tool_name)

    async def execute(self):
        """
        Deactivate yourself. This suspends all of your future capabilities until you are woken up ("activated") again.
        """
        self.vla()

    def deactivate_self(self):
        raise KeyboardInterrupt("Suspending from Suspend VLA_Complex")