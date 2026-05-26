from enum import Enum
from dataclasses import dataclass

class AgencyType(Enum):
    DEMOED = "demoed"
    ARM_VR_DEMO = "arm_vr_demo"
    KEYBOARD_DEMO = "keyboard_demo"
    PASS_TO_AVA = "pass_to_ava"
    AUTO = "auto"
    FIXED = "fixed"
    PASS_THROUGH = "pass_through"
    PASS_TO_UNITY = "pass_to_unity"

class MonitorType(Enum):
    CONDUCT_RECORDING = "conduct_recording"