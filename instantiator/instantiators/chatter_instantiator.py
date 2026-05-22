from ..instantiator import Instantiator
from vla_star_configurable.vla_star_config.vla_star_types import *

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
                if self.try_load_configurable(name_kind):
                    return
                from vla_star_configurable.levels.actuality_levels import Stationary
                from vla_star_configurable.vla_complex_configurable.vla_complex_configurables.chat_configurable import ChatConfigurable
                from vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.chat_config import ChatConfig
                self.configurable = ChatterConfigurable(
                    ChatterConfig(
                        agency_type=AgencyType.AUTO,
                        instructions_type=InstructionType.GOLD,
                        construction_type=ConstructionType.GOLD,
                        motive_type=MotiveType.GOLD,
                    ),
                    Stationary(),
                    None,
                    [
                        ChatConfigurable(
                            ChatConfig(
                                recorded=True
                            ),
                            "chat_tool"
                        )
                    ],
                    name_kind
                )
            case _:
                raise ValueError(discriminator)
            
        self.try_pickle_configurable()
