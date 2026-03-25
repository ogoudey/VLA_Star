from tool_choice_models.model_purveyor import ModelPurveyor
from typing import Callable
from pathlib import Path
import json
def introduction_pipeline(send: Callable, rerun: Callable, introduction_type, name):
    """
    :param send: for hard-coded introductions - goes straight to chat's 'reply'
    :param rerun: for going through the normal rerun request. Can send an internal message which overrides normal context
    :param introduction_type: below for supported introduction types. Set where needed from the OS environ
    :param name: the agent name is passed in here to locate the necessary files
    """
    match introduction_type:
        case "GAME_CSV":
            # dir_path = Path("/path/to/happenings/under/this/name") OR
            context = ""
            ModelPurveyor.introducer("introducer", context)
            pass
        case "CORE":
            rerun({"INTERNAL_MESSAGE": "Introduce yourself to the user, given what you know about yourself. Describe how the user can interact with you, give the observed session history."})
        case _:
            raise ValueError("Introduction type not yet supported.")