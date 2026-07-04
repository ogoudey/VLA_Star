from enum import Enum


class MotiveType(Enum):
    TO_HELP_USER = "to_help_user" # symbiosis via utility-trust
    TO_SABOTAGE = "to_sabotage" # "bad guy" character
    TO_PHILOSOPHIZE = "to_philosophize" # maybe for assessing spatial intelligence?
    MINIMAL = "minimal"
    GOLD = "gold"
    GAME_BOUNCER = ""
    THINKING_OF_A_NUMBER = ""


UNITY_MOTIVE = f"""
Your environment looks like this: There are two gates, gate 1 and gate 2. Each gate is operated by a lever and a pressure plate. The pressure plate opens the gate from the outside and the lever keeps the door open if it's pulled. Inside the inner gate is a pile gold. Your origin/initial position is outside the first gate and across the bridge.

Your job at each moment is to make a single choice, as mentioned. But pay attention to the feedback from the environment, as this will indicate where you are.
"""

MINIMAL_MOTIVE = """
Just vibe.
"""