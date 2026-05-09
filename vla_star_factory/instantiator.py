from ..vla_star_configurable.vla_star_configurable import VLA_Star_Configurable
from vla_star_configurable.vla_star_config.vla_star_types import *

####################################33
#
#   This file needs a description
#
########################################

class Instantiator:
    configurable: VLA_Star_Configurable
    
    class MobileManipulator:
        def __init__(self,
            discriminator: str
        ):
            """
            :param discriminator: "actual" | "unity"
            """
            from ..vla_star_configurable.vla_star_configurables.mobile_manipulator_configurable import MobileManipulatorConfigurable
            from ..vla_star_configurable.vla_star_config.vla_star_configs.mobile_manipulation_config import MobileManipulatorConfig
            
            
            match discriminator.lower().strip():
                case "actual":
                    from ..vla_star_configurable.levels.actuality_levels import Actual
                    from ..vla_star_configurable.morphology.morphologies.ava_gen1 import AvaGen1
                    from ..vla_star_configurable.morphology.morphologies.so101 import SO101
                    from ..vla_star_configurable.morphology.utilities import combine
                    from ..vla_star_configurable.vla_complex_configurable.vla_complex_configurables.so101_manipulation_configurable import SO101ManipulationConfigurable
                    from ..vla_star_configurable.vla_complex_configurable.vla_complex_configurables.ava_gen1_drive_configurable import AvaGen1DriveConfigurable
                    from ..vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.so101_manipulation_demo_config import SO101ManipulationDemoConfig
                    from ..vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.ava_gen1_drive_config import AvaGen1DriveConfig
                    self.configurable = MobileManipulatorConfigurable(
                        MobileManipulatorConfig(
                            agency_type=AgencyType.AUTO,
                            instructions_type=InstructionType.GOLD,
                            construction_type=ConstructionType.GOLD,
                            motive_type=MotiveType.GOLD,
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
                case "unity":
                    from ..vla_star_configurable.levels.actuality_levels import Unity
                    from ..vla_star_configurable.vla_complex_configurable.vla_complex_configurables.unity_arm_configurable import UnityArmConfigurable
                    from ..vla_star_configurable.vla_complex_configurable.vla_complex_configurables.unity_drive_configurable import UnityDriveConfigurable
                    from ..vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.unity_arm_config import UnityArmConfig
                    from ..vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.unity_drive_config import UnityDriveConfig
                    
                    self.configurable = MobileManipulatorConfigurable(
                        MobileManipulatorConfig(
                            auto=False,
                            recorded=False
                        ),
                        Unity(),
                        None,
                        [
                            UnityArmConfigurable(
                                UnityArmConfig(),
                                "arm_tool"
                            ),
                            UnityDriveConfigurable(
                                UnityDriveConfig(),
                                "drive_tool"
                            )
                        ],
                        "mobilemanipulatorinunity"
                    )
                case _:
                    raise ValueError(discriminator)

        def instantiate(self, **kwargs):
            try:
                self.configurable.instantiate(kwargs=kwargs)
            except Exception as e:
                print(f"Failed: {e}")