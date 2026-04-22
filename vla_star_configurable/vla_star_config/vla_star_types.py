from enum import Enum

class MotiveType(Enum):
    TO_HELP_USER = "to_help_user" # symbiosis via utility-trust
    TO_SABOTAGE = "to_sabotage" # "bad guy" character
    TO_PHILOSOPHIZE = "to_philosophize" # maybe for assessing spatial intelligence?
    GOLD = "gold"

class AgencyType(Enum):
    DEMOED = "demoed"
    AUTO = "auto"
    FIXED = "fixed"