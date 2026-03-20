import inspect
import re
import os

IDENTITY_MODEL_STRING = os.environ.get("MOMENT_MODEL_STRING", "o4-mini")
class Tool:

    @staticmethod
    def from_execute(vlac_execute, name: str):
        """
        Takes a
                _________VLA_Complex_________
                            |    
                          execute  ...
        outputs a tool
        
        A list of tools is usable to Model.run
        
        """
        sig = inspect.signature(vlac_execute)
        docstring = vlac_execute.__doc__ or ""
        
        # Parse ":param x: description" or "Args:\n  x: description" style
        param_descriptions = {}
        for match in re.finditer(r":param (\w+):\s*(.+)", docstring):
            param_descriptions[match.group(1)] = match.group(2).strip()

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            param_type = "string"
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"

            properties[param_name] = {
                "type": param_type,
                "description": param_descriptions.get(param_name, "")
            }

            if param.default is inspect._empty:
                required.append(param_name)
        match IDENTITY_MODEL_STRING:
            case "o4-mini":
                return_ = {
                    "type": "function",
                    "name": name,
                    "description": vlac_execute.__doc__.strip() or "",
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                }
            case _:
                return_ = {
                    "type": "function",
                    "name": name,
                    "description": vlac_execute.__doc__.strip() or "",
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                }
        return return_