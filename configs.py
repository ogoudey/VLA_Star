from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional

class RobotType(Enum):
    KINOVA = "kinova"
    SO101 = "so101"
    AVA1 = "ava1"
    NONE = None

class AgencyType(Enum):
    DEMOED = "demoed"
    ARM_VR_DEMO = "arm_vr_demo"
    KEYBOARD_DEMO = "keyboard_demo"
    AUTO = "auto"
    FIXED = "fixed"
    PASS_THROUGH = "pass_through"

class MonitorType(Enum):
    CONDUCT_RECORDING = "conduct_recording"
    
class VLAType(Enum):
    ACTUATION = "actuation"
    TEXT = "text"

@dataclass
class RobotConfig:
    robot_type: RobotType

@dataclass
class AgencyConfig:
    agency_type: AgencyType
    recorded: bool

@dataclass
class VLAComplexConfig:
    vla_type: VLAType
    agency_type: AgencyType
    monitor_types: Optional[List[MonitorType]]
    recorded: bool