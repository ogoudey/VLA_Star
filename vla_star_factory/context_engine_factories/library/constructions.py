from enum import Enum

class ConstructionType(Enum):
    TO_HELP_USER = "to_help_user" # symbiosis via utility-trust
    TO_SABOTAGE = "to_sabotage" # "bad guy" character
    TO_PHILOSOPHIZE = "to_philosophize" # maybe for assessing spatial intelligence?
    YOURE_STATIONARY = "youre_stationary"
    GOLD = "gold"

CONSTRUCTION1 = """
You are a decision-making agent in a network of LLMs that compose a physical agent. Respond appropriately to the context by supplying adequate arguments to a function.
"""
import vla_star_factory.context_engine_factories.context_engine_factory_utilities.platform_description as platform_description

YOURE_STATIONARY = f"""
You are an LLM model running in {platform_description}. You cannot move and jsut get woken up occasionally.
"""