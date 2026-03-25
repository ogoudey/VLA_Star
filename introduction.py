from tool_choice_models.model_purveyor import ModelPurveyor
from typing import Callable
from pathlib import Path
import json
def introduction_pipeline(send: Callable, rerun: Callable, introduction_type, name):
    match introduction_type:
        case "GAME_CSV":
            # dir_path = Path("/path/to/happenings/under/this/name") OR
            context = ""
            ModelPurveyor.introducer("introducer", context)
            pass
        case "CORE":
            rerun({"INTERNAL_MESSAGE": "Introduce yourself to the user, given what you know about yourself. Describe how the user can interact with you, give the observed session history."})
    