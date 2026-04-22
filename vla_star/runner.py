import queue



import asyncio
import json
from gda import OrderedContextLLMAgent
from displays import log, timestamp, update_activity

class ThinkingMachine:
    """ Convenience class in charge of dishing out LLM calls """
    def __init__(self, prototype: OrderedContextLLMAgent):
        self.reruns = queue.Queue()
        self.prototype = prototype

        self.updated = False

        self.active = False
    
    def __str__(self):
        return f"ThinkingMachine"

    def rerun(self, source):
        if source == "STOP":
            self.active = False
            print("STOPPING")
        

        # Common Case
        self.reruns.put(source)
    
    async def start(self):
        print("Thinking Machine starting...")
        loop = asyncio.get_running_loop()
        self.active = True
        while self.active:
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
            if type(source) == dict: # here it's a structured message - why? well only exceptions are not general context, the request()
                try:
                    asyncio.create_task(self.prototype.request(source["INTERNAL_MESSAGE"]))
                except KeyError as e:
                    raise Exception(f"Internal message '{source}' not supported.")
                continue    
            asyncio.create_task(self.prototype.request())
        print(f"Thinking Machine ending.")