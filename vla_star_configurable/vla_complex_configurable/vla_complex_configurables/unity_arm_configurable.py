from ..vla_complex_configurable import VLA_Complex_Configurable
from ..vla_complex_config.vla_complex_configs.unity_arm_config import UnityArmConfig

class UnityArmConfigurable(VLA_Complex_Configurable):
    def __init__(self,
        vla_complex_config: UnityArmConfig,
        name: str
    ):
        super().__init__(
            vla_complex_config,
            name
        )
    
    def instantiate(self):
        from vla_complex.vla_complexes.unity_drive import UnityDrive
        return UnityDrive("drive")
