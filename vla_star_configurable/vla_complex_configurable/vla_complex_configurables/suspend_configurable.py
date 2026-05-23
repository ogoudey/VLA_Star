from ..vla_complex_configurable import VLA_Complex_Configurable
from ..vla_complex_config.vla_complex_configs.suspend_config import SuspendConfig
from vla_complex.vla_complex import VLA_Complex

class SuspendConfigurable(VLA_Complex_Configurable):
    def __init__(self,
        vla_complex_config: SuspendConfig,
        name: str
    ):
        super().__init__(
            vla_complex_config,
            name
        )
    
    def instantiate(self, **kwargs) -> VLA_Complex:
        return self.instantiate_with_filtered_args(self.vla_complex_config.instantiate, kwargs)
