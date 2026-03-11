from pathlib import Path
from typing import Any, TypeAlias, Union
import json
from displays import log, show_context, timestamp
from context_utils import OrderedContext
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from agents import RunResult, ToolCallItem


JsonValue: TypeAlias = Union[dict[str, "JsonValue"], list["JsonValue"], str, int, float, bool, None]

def json_dict() -> dict[str, JsonValue]:
    return {}

@dataclass
class ToolChoiceMade:
    type: str = "function"
    function: dict = field(default_factory=dict)

class Dataset:
    filepath: Path
    current_frame: defaultdict[str, JsonValue] = defaultdict(json_dict)    
    
    def __init__(self, name):
        datasets_dir = Path("data/multi")
        if not datasets_dir.exists():
            datasets_dir.mkdir(parents=True, exist_ok=True)
        self.filepath = datasets_dir / f"{name}@{timestamp()}.json"


    def end_frame(self):
        with open(self.filepath, "w") as f:
            f.write(json.dumps(self.current_frame))

    def timestamp_frame(self):
        self.current_frame["timestamp"] = datetime.now(timezone.utc).isoformat()

    def add_metadata_to_frame(self, metadata: dict):
        self.current_frame["metadata"] = metadata

    def add_to_frame(self, subframe: Any):
        if self.current_frame is None:
            self.current_frame = defaultdict(dict)
            self.current_frame["messages"] = []
        match subframe:
            case OrderedContext():
                self.current_frame["messages"].append({
                    "role": "user",
                    "content": str(subframe)
                })
            case str():  # instructions
                self.current_frame["messages"].append({
                    "role": "system",
                    "content": subframe
                })
            case list():  # tools
                self.current_frame["tools"] = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.params_json_schema,
                        },
                    }
                    for tool in subframe
                ]
            case RunResult():
                tool_choices = parse_tool_choices(subframe)
                self.current_frame["tool_choice_made"] = tool_choices[0] if len(tool_choices) == 1 else tool_choices
            case ToolChoiceMade():
                self.current_frame["tool_choice_made"] = asdict(subframe)
            case _:
                raise TypeError(f"add_to_frame: unsupported type {type(subframe)}")

def parse_tool_choices(result: RunResult) -> list[JsonValue]:
    """Utility for squeezing just this out of a OpenAI RunResult"""
    return [
        {
            "type": "function",
            "function": {
                "name": item.raw_item.name,
                "arguments": item.raw_item.arguments,  # already a JSON string
            }
        }
        for item in result.new_items
        if isinstance(item, ToolCallItem)
    ]



        


"""
I take in:
- instructions (system prompt)
- context (essentially user prompt)
- user prompt (essentially context)
- I can get the tools. Any easy way to access them given that I have a list of (OpenAI AgentsSDK) function_tool 
- I still need to measure the latency
- outcome?
- model is o4-mini
"""



"""
{
✅  "timestamp": "2026-03-11T10:00:00Z",
✅  "messages": [
✅   {"role": "system", "content": "You are a helpful assistant with tools."}, ✅
✅   {"role": "user", "content": "What's the weather in Boston?"} ✅
✅  ],
✅  "tools": [
✅    {
✅      "type": "function",
✅      "function": {
✅        "name": "get_weather",
✅        "description": "Get current weather for a city",
✅        "parameters": {
✅          "type": "object",
✅          "properties": {
✅            "city": {"type": "string"}
✅          }
✅        }
✅      }
✅    }
✅  ],
✅  "tool_choice_made": {
✅    "type": "function",
✅    "function": {
✅      "name": "get_weather",
✅      "arguments": "{\"city\": \"Boston\"}"
✅    }
✅  },
  "metadata": {
    "model": "o4-mini",
    "latency_ms": 340,
    "outcome": null
  }
}
"""