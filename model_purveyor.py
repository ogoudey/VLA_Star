from agents import Agent, Runner, function_tool, FunctionTool
from typing import List
import os
from model_output_types import SummarizedSessions
import json
# =============== #
#      ROLES      #

IDENTITY_MODEL_STRING = os.environ.get("MOMENT_MODEL_STRING", "o4-mini")
SUMMARIZER_MODEL_STRING = os.environ.get("MEMORY_MODEL_STRING", "o4-mini")

from model import Model

if not IDENTITY_MODEL_STRING == "o4-mini":
    from agents.extensions.models.litellm_model import LitellmModel

class ModelPurveyor:
    IDENTITY_MODEL_STRING = IDENTITY_MODEL_STRING
    SUMMARIZER_MODEL_STRING = SUMMARIZER_MODEL_STRING
    
    @staticmethod
    def identity(name: str, instructions: str, function_tools: List[dict]):
        match IDENTITY_MODEL_STRING:
            case "o4-mini":
                return Model(
                    name=name,
                    instructions=instructions,
                    tools=function_tools, # The tool-ified VLA Complexes
                    model="o4-mini"
                )
            case "claude-sonnet-4-20250514":
                return Model(
                    name=name,
                    instructions=instructions,
                    tools=function_tools, # The tool-ified VLA Complexes
                    model=LitellmModel(model="anthropic/claude-sonnet-4-20250514")
                )
        

    @staticmethod
    async def run(identity, context, tool_dispatcher):
        match IDENTITY_MODEL_STRING:
            case "o4-mini":
                result = await identity.run(context)
            case "claude-sonnet-4-20250514":
                result = await identity.run(context)
        
        match IDENTITY_MODEL_STRING:
            case "o4-mini":
                for i, item in enumerate(result.output):
                    print(f"Result output {i}. {item}")
                    if item.type == "function_call":
                        if not item.arguments or item.arguments == '{}':
                            print("⚠️ Empty arguments, skipping:", item)
                            continue
                        await tool_dispatcher[item.name](**json.loads(item.arguments))
            case "claude-sonnet-4-20250514":
                for tool_call in result.choices[0].message.tool_calls:
                    await tool_dispatcher[tool_call.function.name](**json.loads(tool_call.function.arguments))
            
    @staticmethod
    def summarizer(name: str, instructions: str):
        match SUMMARIZER_MODEL_STRING:
            case "o4-mini":
                return Agent(
                    name=name,
                    instructions=instructions,
                    model="o4-mini",
                    output_type=SummarizedSessions
                )
            case "claude-sonnet-4-20250514":
                return Agent(
                    name=name,
                    instructions=instructions,
                    model=LitellmModel(model="anthropic/claude-sonnet-4-20250514"),
                    output_type=SummarizedSessions
                )
            
    @staticmethod
    async def remember(identity, context):
        match SUMMARIZER_MODEL_STRING:
            case "o4-mini":
                return await Runner.run(identity, context)
            case "claude-sonnet-4-20250514":
                return await Runner.run(identity, context)