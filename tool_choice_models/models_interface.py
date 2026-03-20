import litellm
from openai import AsyncOpenAI
client = AsyncOpenAI()  # automatically uses OPENAI_API_KEY

"""
Implements run methods
"""

class Model:
    def __init__(self, name, instructions, tools, model):
        self.name = name
        self.instructions = instructions
        self.tools = tools
        self.model = model

    async def run(self, input):
        # Detect provider style
        print(f"Tools right before client.responses.create: {self.tools}")
        if isinstance(self.model, str):
            # OpenAI native
            return await client.responses.create(
                model=self.model,
                instructions=self.instructions,
                input=input,
                tools=self.tools
            )
        else:
            # LiteLLM or other provider
            return await litellm.acompletion(
                model=self.model.model,
                messages=[
                    {"role": "system", "content": self.instructions},
                    {"role": "user", "content": input},
                ],
                tools=self.tools,
                tool_choice="required",  # may vary slightly by provider
            )