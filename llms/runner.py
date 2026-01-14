import queue



import asyncio
from agents import Runner

from gda import GDA
from displays import log, timestamp, update_activity

class ThinkingMachine:
    """ Convenience class """
    def __init__(self, prototype: GDA):
        self.reruns = queue.Queue()
        self.prototype = prototype

        self.updated = False
    
    def __str__(self):
        return f"ThinkingMachine"

    def rerun(self, rerun_input, signature):
        print(f"Rerun request from {signature}")
        self.reruns.put((rerun_input, signature))
    
    async def start(self):
        print("Thinking Machine starting...")
        loop = asyncio.get_running_loop()
        while True:
            if not self.updated:
                update_activity("ThinkingMachine idle.", self)
            try:
                rerun_input, source = self.reruns.get_nowait()
                update_activity("Thinking...", self) # Never gets here (good)
            except queue.Empty:
                await asyncio.sleep(0.1)  # throttle
                continue
            print(f"Running agent!")
            # Fire-and-forget agent
            asyncio.create_task(self.run_agent(rerun_input, source))

    

    async def run_agent(self, rerun_input, source):
        context = self.prototype.context_from(rerun_input, source)
        update_activity("Processing user input...", f"{source} interpretation")
        await self.prototype.run_identity(context) # could be neater
        update_activity("Done processing user input...", f"{source} interpretation", exit=True)
