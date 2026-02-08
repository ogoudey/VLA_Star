import queue



import asyncio

from gda import OrderedContextLLMAgent
from displays import log, timestamp, update_activity

class ThinkingMachine:
    """ Convenience class """
    def __init__(self, prototype: OrderedContextLLMAgent):
        self.reruns = queue.Queue()
        self.prototype = prototype

        self.updated = False
    
    def __str__(self):
        return f"ThinkingMachine"

    def rerun(self, source):
        self.reruns.put(source)
    
    async def start(self):
        print("Thinking Machine starting...")
        loop = asyncio.get_running_loop()
        while True:
            if not self.updated:
                update_activity("ThinkingMachine idle.", self)
            try:
                source = self.reruns.get_nowait()
                update_activity("Thinking...", self) # Never gets here (good)
            except queue.Empty:
                await asyncio.sleep(0.1)  # throttle
                continue
            print(f"{source} runs agent!")
            # Fire-and-forget agent
            asyncio.create_task(self.prototype.request())

    

