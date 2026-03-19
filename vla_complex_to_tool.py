import inspect


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

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            # VERY basic typing (improve this later)
            param_type = "string"
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"

            properties[param_name] = {"type": param_type}

            if param.default is inspect._empty:
                required.append(param_name)

        return_ = {
            "name": name,
            "type": "function",
            "function": {
                "name": name,
                "description": vlac_execute.__doc__ or "",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
        return return_