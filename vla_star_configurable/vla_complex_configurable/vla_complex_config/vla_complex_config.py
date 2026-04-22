from .vla_complex_types import *
from typing import Optional, List

class VLA_Complex_Config:
    agency_type: AgencyType
    monitor_types: List[MonitorType]
    recorded: bool

    def __init__(self,
        agency_type: AgencyType,
        monitor_types: List[MonitorType],
        recorded: bool
    ):
        self.agency_type = agency_type
        self.monitor_types = monitor_types
        self.recorded = recorded
