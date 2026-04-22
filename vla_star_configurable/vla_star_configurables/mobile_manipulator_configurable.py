from typing import List
from ..vla_star_configurable import VLA_Star_Configurable
from ..vla_star_config.vla_star_configs.mobile_manipulation_ava_gen1_so101_config import MobileManipulatorAvaGen1SO101Config
from ..levels.actuality_levels import Actual

from ..morphology.morphologies.ava_gen1 import AvaGen1
from ..morphology.morphologies.so101 import SO101
from ..morphology.morphology import Morphology
from ..morphology.utilities import combine

from ..vla_complex_configurable.vla_complex_configurables.so101_manipulation_configurable import SO101ManipulationConfigurable
from ..vla_complex_configurable.vla_complex_configurables.ava_gen1_drive_configurable import AvaGen1DriveConfigurable
from ..vla_complex_configurable.vla_complex_configurable import VLA_Complex_Configurable

from vla_star.vla_star import VLA_Star

class MobileManipulatorConfigurable(VLA_Star_Configurable):
    def __init__(self,
        config: MobileManipulatorAvaGen1SO101Config,
        actuality: Actual,
        morphology: Morphology,
        vla_complex_configurables: List[VLA_Complex_Configurable],
        name: str,    
    ):
        super().__init__(
            config,
            actuality,
            morphology,
            vla_complex_configurables,
            name
        )

    def build(self):
        from vla_star_factory.vla_star_factory import build_mobile_manipulator_agent
        agent = build_mobile_manipulator_agent(self.config)
        vla_complexes = []
        for vla_complex_configuration in self.vla_complex_configurables:
            vla_complexes.append(vla_complex_configuration.build())
        agent.link_vla_complexes(vla_complexes)
        return VLA_Star(agent, vla_complexes) 