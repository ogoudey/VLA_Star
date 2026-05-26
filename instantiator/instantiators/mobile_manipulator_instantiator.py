from ..instantiator import Instantiator
from vla_star_configurable.vla_star_config.vla_star_types import *
from vla_star_factory.context_engine_factories.library.instructions import *
from vla_star_factory.context_engine_factories.library.constructions import *
from vla_star_factory.context_engine_factories.library.motives import *
class MobileManipulatorInstantiator(Instantiator):
    def __init__(self,
        discriminator: str
    ):
        """
        :param discriminator: "actual" | "unity"
        """
        from vla_star_configurable.vla_star_configurables.mobile_manipulator_configurable import MobileManipulatorConfigurable
        from vla_star_configurable.vla_star_config.vla_star_configs.mobile_manipulator_config import MobileManipulatorConfig
        
        
        match discriminator.lower().strip():
            # SPECIES
            case "actual":
                name_kind = "mobilemanipulatorwithso101onanavagen1"
                if self.try_load_configurable(name_kind):
                    return
                from vla_star_configurable.levels.actuality_levels import Actual
                from vla_star_configurable.morphology.morphologies.ava_gen1 import AvaGen1
                from vla_star_configurable.morphology.morphologies.so101 import SO101
                from vla_star_configurable.morphology.utilities import combine
                from vla_star_configurable.vla_complex_configurable.vla_complex_configurables.so101_manipulation_configurable import SO101ManipulationConfigurable
                from vla_star_configurable.vla_complex_configurable.vla_complex_configurables.ava_gen1_drive_configurable import AvaGen1DriveConfigurable
                from vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.so101_manipulation_demo_config import SO101ManipulationDemoConfig
                from vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.ava_gen1_drive_config import AvaGen1DriveConfig
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
                    name_kind
                )
            case "unity":
                name_kind = "mobilemanipulatorinunity"
                if self.try_load_configurable(name_kind):
                    return
                from vla_star_configurable.levels.actuality_levels import Unity
                from vla_star_configurable.vla_complex_configurable.vla_complex_configurables.arm_configurable import UnityArmConfigurable
                from vla_star_configurable.vla_complex_configurable.vla_complex_configurables.unity_drive_configurable import UnityDriveConfigurable
                from vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.arm_config import UnityArmConfig
                from vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.unity_drive_config import UnityDriveConfig
                
                self.configurable = MobileManipulatorConfigurable(
                    MobileManipulatorConfig(
                        agency_type=AgencyType.AUTO,
                        instructions_type=InstructionType.GOLD,
                        construction_type=ConstructionType.GOLD,
                        motive_type=MotiveType.GOLD,
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
                    name_kind 
                )
            case _:
                raise ValueError(discriminator)
            
        self.try_pickle_configurable()
