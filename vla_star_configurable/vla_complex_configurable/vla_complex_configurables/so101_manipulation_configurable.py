from ..vla_complex_configurable import VLA_Complex_Configurable

from ..vla_complex_config.vla_complex_configs.so101_manipulation_demo_config import SO101ManipulationDemoConfig



class SO101ManipulationConfigurable(VLA_Complex_Configurable):
    def __init__(self,
        vla_complex_config: SO101ManipulationDemoConfig,
        name: str
    ):
        super().__init__(
            vla_complex_config,
            name
        )
    
    def instantiate(self):
        from utilities.import_helper import find
        vla_interface_module = find("vla_interface")
        runner = vla_interface_module.factory_function(self.vla_complex_config)

        from vla_complex.vla_complexes.episodic_recorder import EpisodicRecorder
        return EpisodicRecorder(runner, "record_conductor")
