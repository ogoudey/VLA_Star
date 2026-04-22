from typing import Optional
from ..vla_star_configurable.vla_star_configurable import VLA_Star_Configurable

class Instantiator:
    configuration: VLA_Star_Configurable
    @staticmethod
    def configure_mobile_manipulator():
        from ..vla_star_configurable.vla_star_configurables.mobile_manipulator_configurable import MobileManipulatorConfigurable
        from ..vla_star_configurable.vla_star_config.vla_star_configs.mobile_manipulation_ava_gen1_so101_config import MobileManipulatorAvaGen1SO101Config
        from ..vla_star_configurable.levels.actuality_levels import Actual
        from ..vla_star_configurable.morphology.morphologies.ava_gen1 import AvaGen1
        from ..vla_star_configurable.morphology.morphologies.so101 import SO101
        from ..vla_star_configurable.morphology.utilities import combine
        from ..vla_star_configurable.vla_complex_configurable.vla_complex_configurables.so101_manipulation_configurable import SO101ManipulationConfigurable
        from ..vla_star_configurable.vla_complex_configurable.vla_complex_configurables.ava_gen1_drive_configurable import AvaGen1DriveConfigurable
        from ..vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.so101_manipulation_demo_config import SO101ManipulationDemoConfig
        from ..vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.ava_gen1_drive_config import AvaGen1DriveConfig

        return MobileManipulatorConfigurable(
            MobileManipulatorAvaGen1SO101Config(
                auto=False,
                recorded=False
            ),
            Actual(),
            combine(AvaGen1(), SO101()),
            [
                SO101ManipulationConfigurable(
                    SO101ManipulationDemoConfig(
                        dataset_name="test_dataset",
                        recorded=True
                    ),
                    "arm_tool"
                ),
                AvaGen1DriveConfigurable(
                    AvaGen1DriveConfig(),
                    "drive_tool"
                )
            ],
            "mobilemanipulatorwithso101onanavagen1"
        )
    
    def __init__(self, configuration: VLA_Star_Configurable):
        self.configuration = configuration

    def instantiate(self):
        self.configuration.build()