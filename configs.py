from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

class RobotType(Enum):
    KINOVA = "kinova"
    SO101 = "so101"
    UNITY = "unity"
    AVA1 = "ava1"
    NONE = None

class AgencyType(Enum):
    DEMOED = "demoed"
    ARM_VR_DEMO = "arm_vr_demo"
    KEYBOARD_DEMO = "keyboard_demo"
    PASS_TO_AVA = "pass_to_ava"
    AUTO = "auto"
    FIXED = "fixed"
    PASS_THROUGH = "pass_through"
    PASS_TO_UNITY = "pass_to_unity"
    SCHEDULER = "scheduler"

class MonitorType(Enum):
    CONDUCT_RECORDING = "conduct_recording"
    
class VLAType(Enum):
    NAVIGATION = "navigation"
    MANIPULATION = "manipulation"
    TEXT_USER = "text_user"
    AVA_DRIVE = "ava_drive"
    AVA_TAGGING = "ava_tagging"
    PROCESS = "process"


class MotiveType(Enum):
    TO_HELP_USER = "to_help_user" # symbiosis via utility-trust
    TO_SABBOTAGE_USER = "to_sabbotage_user" # "bad guy" character
    TO_PHILOSOPHIZE = "to_philosophize" # maybe for assessing spatial intelligence?

@dataclass
class RobotConfig:
    robot_type: RobotType

@dataclass
class AgencyConfig:
    agency_type: AgencyType
    recorded: bool=False
    motive_type: Optional[MotiveType] = None
    # long_term_memory: bool = False

@dataclass
class VLAComplexConfig:
    vla_type: VLAType
    agency_type: AgencyType
    monitor_types: Optional[List[MonitorType]]
    robot_type: Optional[RobotType]=None
    policy_path: Optional[Path] = None
    dataset_name: Optional[str] = None
    recorded: bool=False