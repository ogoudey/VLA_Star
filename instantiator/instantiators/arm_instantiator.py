from ..instantiator import Instantiator
from vla_star_configurable.vla_star_config.vla_star_types import *
from vla_star_factory.context_engine_factories.library.instructions import *
from vla_star_factory.context_engine_factories.library.constructions import *
from vla_star_factory.context_engine_factories.library.motives import *

class ArmInstantiator(Instantiator):
    def __init__(self,
        discriminator: str
    ):
        """
        :param discriminator: "norm"
        """
        from vla_star_configurable.vla_star_configurables.arm_user_configurable import ArmUserConfigurable
        from vla_star_configurable.vla_star_config.vla_star_configs.chatter_config import ChatterConfig
        
        
        match discriminator.lower().strip():
            # SPECIES
            case "unityUR5":
                name_kind = "chatteragentunityUR5"
                if self.try_load_configurable(name_kind):
                    return
                from vla_star_configurable.morphology.morphologies.so101 import SO101
                from vla_star_configurable.levels.actuality_levels import Unity
                from vla_star_configurable.vla_complex_configurable.vla_complex_configurables.chat_template import ChatConfigurable
                from vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.comms_config import ChatConfig
                from vla_star_configurable.vla_complex_configurable.vla_complex_configurables.arm_configurable import ArmConfigurable
                from vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.arm_config import ArmConfig
                from vla_star_configurable.vla_complex_configurable.vla_complex_configurables.suspend_configurable import SuspendConfigurable
                from vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_configs.suspend_config import SuspendConfig

                self.configurable = ArmUserConfigurable(
                    ChatterConfig(
                        agency_type=AgencyType.DEMOED,
                        instructions_type=InstructionType.MINIMAL,
                        construction_type=ConstructionType.YOURE_STATIONARY,
                        motive_type=MotiveType.MINIMAL,
                    ),
                    Unity(),
                    SO101(),
                    [
                        ChatConfigurable(
                            ChatConfig(
                                recorded=True,
                                chat_port=5001
                            ),
                            "chat_tool"
                        ),
                        ArmConfigurable(
                            ArmConfig(
                                recorded=True,
                                demoed=True
                                teleop_port=5004
                            ),
                            "arm_tool"
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
