from ..instantiator import Instantiator
from vla_star_configurable.vla_star_config.vla_star_types import *
from vla_star_factory.context_engine_factories.library.instructions import *
from vla_star_factory.context_engine_factories.library.constructions import *
from vla_star_factory.context_engine_factories.library.motives import *

class ChatterInstantiator(Instantiator):
    def __init__(self,
        discriminator: str
    ):
        """
        :param discriminator: "norm"
        """
        from vla_star_configurable.vla_star_configurables.chatter_configurable import ChatterConfigurable
        from vla_star_configurable.vla_star_config.vla_star_configs.chatter_config import ChatterConfig
        
        
        match discriminator.lower().strip():
            # SPECIES
            case "norm":
                name_kind = "chatteragentfortestingmostly"
                super().__init__()
                if self.configurable:
                    return
                from vla_star_configurable.levels.actuality_levels import Stationary
                from vla_star_configurable.vla_complex_template.vla_complex_templates.chat_template import ChatConfigurable
                from vla_star_configurable.vla_complex_template.vla_complex_config.vla_complex_configs.comms_config import ChatConfig
                from vla_star_configurable.vla_complex_template.vla_complex_templates.suspend_template import SuspendConfigurable
                from vla_star_configurable.vla_complex_template.vla_complex_config.vla_complex_configs.suspend_config import SuspendConfig

                self.configurable = ChatterConfigurable(
                    ChatterConfig(
                        agency_type=AgencyType.AUTO,
                        instructions_type=InstructionType.MINIMAL,
                        construction_type=ConstructionType.YOURE_STATIONARY,
                        motive_type=MotiveType.MINIMAL,
                    ),
                    Stationary(),
                    None,
                    [
                        ChatConfigurable(
                            ChatConfig(
                                recorded=True,
                                chat_port=5001
                            ),
                            "chat_tool"
                        ),
                        SuspendConfigurable(
                            SuspendConfig(

                            ),
                            "suspend_tool"
                        )
                    ],
                    name_kind
                )
            case _:
                raise ValueError(discriminator)
            
        self.try_pickle_configurable()
