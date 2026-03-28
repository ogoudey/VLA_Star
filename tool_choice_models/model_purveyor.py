"""
Purveys models from model providers, according to the methods herein, according to the env variable.
"""
from agents import Agent, Runner
from typing import List
import os
from tool_choice_models.output_types import SummarizedSessions
import json
from tool_choice_models.models_interface import Model

IDENTITY_MODEL_STRING = os.environ.get("MOMENT_MODEL_STRING", "o4-mini")
SUMMARIZER_MODEL_STRING = os.environ.get("MEMORY_MODEL_STRING", "o4-mini")
INTRODUCER_MODEL_STRING = os.environ.get("INTRODUCER_MODEL_STRING", "o4-mini")

from agents.extensions.models.litellm_model import LitellmModel

class ModelPurveyor:
    IDENTITY_MODEL_STRING = IDENTITY_MODEL_STRING
    SUMMARIZER_MODEL_STRING = SUMMARIZER_MODEL_STRING
    INTRODUCER_MODEL_STRING = INTRODUCER_MODEL_STRING
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
        print("Running LLM...")
        match IDENTITY_MODEL_STRING:
            case "o4-mini":
                result = await identity.run(context)
            case "claude-sonnet-4-20250514":
                result = await identity.run(context)
        print("Executing tools...")
        match IDENTITY_MODEL_STRING:
            case "o4-mini":
                for i, item in enumerate(result.output):
                    print(f"Result output {i}. {item}")
                    if item.type == "function_call": # Grabs the first one - if two is made - doesn't matter
                        if not item.arguments or item.arguments == '{}':
                            print("⚠️ Empty arguments, skipping:", item)
                            continue
                        await tool_dispatcher[item.name](**json.loads(item.arguments))
                        return item.name, json.loads(item.arguments), 
            case "claude-sonnet-4-20250514":
                for tool_call in result.choices[0].message.tool_calls:
                    await tool_dispatcher[tool_call.function.name](**json.loads(tool_call.function.arguments))
            case _:
                return "default_name", {}
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
    
    @staticmethod
    def introducer(name: str, instructions: str):
        match INTRODUCER_MODEL_STRING:
            case "o4-mini":
                return Agent(
                    name=name,
                    instructions=instructions,
                    model="o4-mini"
                )
            case "claude-sonnet-4-20250514":
                return Agent(
                    name=name,
                    instructions=instructions,
                    model=LitellmModel(model="anthropic/claude-sonnet-4-20250514")
                )
            
    @staticmethod
    async def introduce(identity, context):
        match SUMMARIZER_MODEL_STRING:
            case "o4-mini":
                return await Runner.run(identity, context)
            case "claude-sonnet-4-20250514":
                return await Runner.run(identity, context)