from ..vla_complex import VLA_Complex


class Suspend(VLA_Complex):

    def __init__(self):
        super().__init__("suspend", False)

    async def execute(self):
        """
        Deactivate yourself. This suspends all of your future capabilities until you are woken up ("activated") again.
        """
        self.deactivate_self()

    def deactivate_self(self):
        raise KeyboardInterrupt("Suspending from Suspend VLA_Complex")