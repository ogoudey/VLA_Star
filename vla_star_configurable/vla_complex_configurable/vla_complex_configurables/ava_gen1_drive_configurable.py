from ..vla_complex_configurable import VLA_Complex_Configurable
from ..vla_complex_config.vla_complex_configs.ava_gen1_drive_config import AvaGen1DriveConfig

class AvaGen1DriveConfigurable(VLA_Complex_Configurable):
    def __init__(self,
        vla_complex_config: AvaGen1DriveConfig,
        name: str
    ):
        pass

    def instantiate(self):
        from utilities.import_helper import find
        ava_base_module = find("ava_base")
        from vla_complex.vla_complexes.ava_drive import AvaDrive
        return AvaDrive(ava_base_module, "drive")