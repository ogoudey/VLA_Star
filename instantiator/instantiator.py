from pathlib import Path

from vla_star_configurable.vla_star_configurable import VLA_Star_Configurable
from vla_star_configurable.vla_star_config.vla_star_types import *

class Instantiator:
    configurable: VLA_Star_Configurable
    frozen_encoded_configurables: Path = Path("frozen") / "configurables"
    frozen_vla_stars: Path = Path("frozen") / "vla_stars"

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
                from vla_star_configurable.vla_complex_configurable.vla_complex_configurables.unity_arm_configurable import UnityArmConfigurable
                from vla_star_configurable.vla_complex_configurable.vla_complex_configurables.unity_drive_configurable import UnityDriveConfigurable
                from vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.unity_arm_config import UnityArmConfig
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

    def instantiate(self, **kwargs):
        print("Instantiating...")
        vla_star = self.configurable.instantiate(**kwargs)
        try:
            self.try_pickle_vla_star(vla_star)
        except Exception as e:
            print(f"Failed: {e}")


    def try_pickle_configurable(self):
        try:
            import pickle
            if not self.frozen_encoded_configurables.exists():
                self.frozen_encoded_configurables.mkdir(parents=True, exist_ok=True)
            with open(self.frozen_encoded_configurables / f"{self.configurable.name_kind}.pkl", 'wb') as f:  # Overwrites any existing file.
                pickle.dump(self.configurable, f, pickle.HIGHEST_PROTOCOL)
        except ImportError:
            print(f"Failed to pickle {self.configurable.name_kind}... skipping.")

    def try_load_configurable(self, name_kind):
        try:
            import pickle
            with open(self.frozen_encoded_configurables / f"{name_kind}.pkl", 'rb') as f:
                self.configurable = pickle.load(f)
            print(f"Using existing code for {name_kind}.")
            return True
        except ImportError:
            return False #silent

    def try_pickle_vla_star(self, vla_star):
        try:
            import pickle
            if not self.frozen_vla_stars.exists():
                self.frozen_vla_stars.mkdir(parents=True, exist_ok=True)
            with open(self.frozen_vla_stars / f"{vla_star.name}.pkl", 'wb') as f:  # Overwrites any existing file.
                pickle.dump(self.configurable, f, pickle.HIGHEST_PROTOCOL)
        except ImportError:
            print(f"Failed to pickle the {self.configurable.name_kind} named {vla_star.name}... skipping.")
