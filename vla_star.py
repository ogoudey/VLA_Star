from typing import List
import asyncio

from gda import GDA
from vla_complex import VLA_Complex


class VLA_Star:
    agent: GDA
    vla_complexes: List[VLA_Complex]

    def __init__(self, agent: GDA, vla_complexes: List[VLA_Complex]):
        self.agent = agent
        self.agent.set_tools(vla_complexes)

    def run(self, prompt: str | None = None):
        asyncio.run(self.agent.run(prompt))

"""
### Demos ###
def street_and_crosswalks():
    driving_monitor = VLM("driving_monitor", "You are the perception system for a car, noting the status of a mission. Given the query, return either OK or a descriptive response.")

    agent = GDA("decision-maker", None, \
    "You are a decision-making agent in a network of LLMs that compose a physical agent. Your ultimate goal is to safely drive down the street. To do so you must call your function. However, you can only reach your goal one step at a time. Return one and ONLY one \"step\" of your journey. Your final output doesn't matter, only the one function call. Simple!" \
    "")

                    
    vla = SimpleDrive()

    driver = VLA_Complex("drive", agent, driving_monitor, vla, \
    "Use a model to perform the instruction. Only make one tool call. This model's capabilities are to go forward, turn an angle, or halt:" \
    "" \
    "instruction: \"forward\" | \"turn +n\" (degrees to the right)| \"turn -n\" (degrees to the left)| \"stop\"" \
    "A turn will only apply once. It will not repeat unless you provide a new angle.")
    
    agent.set_drivers([driver])

    drive = VLA_Star("drive_down_the_street", driving_monitor, agent)

    asyncio.run(drive.run("Drive safely, obeying the rules of the road (MA law)."))

def navigate_river():
    driving_monitor = VLM("driving_monitor", system_prompt="You are the perception system for a boat, and take note of the status of the mission. Given the query, return either OK or a descriptive response. (The boat can only go forward, turn in units degrees, or stop, and is very unmaneuverable.)",
                          recommendation_system_prompt="You are a navigation system for a boat, suggesting \"forward\", \"turn left n\", \"turn right n\", or \"stop\".")

    agent = GDA("decision-maker", None, \
    "You are a decision-making agent in a network of LLMs that compose a physical agent. Your ultimate goal is to navigate through the narrow brook safely (without hitting any land).\n" \
    "You may choose ANY of the available tools.\n"\
    "You must call exactly ONE tool.\n"\
    "After calling one tool, stop all further reasoning.\n"\
    "Do not produce natural-language output. "\
    "Return immediately after the tool call.\n")

                    
    vla = SimpleDrive()

    driver = VLA_Complex("drive", agent, driving_monitor, vla, \
    "Use a model to perform the instruction. Only make one tool call. This model's capabilities are to go forward, turn slightly (will keep moving), or halt:" \
    "" \
    "instruction: \"forward\" | \"turn left n\"| \"turn right n\"| \"stop\"")

    agent.set_drivers([driver])

    drive = VLA_Star("navigate_through_the_river", driving_monitor, agent)

    asyncio.run(drive.run("Navigate safely through the narrow brook."))

def follow_path_river():
    driving_monitor = VLM("driving_monitor", system_prompt="You are the perception system for a boat. Take note of the status of the mission. Given the query, return either OK or a descriptive response.")

    agent = GDA("decision-maker", None, \
    "You are a decision-making agent in a network of LLMs that compose a physical agent. Your ultimate goal is to navigate through the narrow brook safely (without hitting any land).\n" \
    "You may choose ANY of the available tools.\n"\
    "You must call exactly ONE tool.\n"\
    "After calling one tool, stop all further reasoning.\n"\
    "Do not produce natural-language output. "\
    "Return immediately after the tool call.\n")

                    
    vla = PathFollow()

    driver = VLA_Complex("drive", agent, driving_monitor, vla, \
    "Use a model to perform the instruction. Only make one tool call. This model's capabilities are to go to a locations from the following list:" \
    "dockA, dockB, center_of_pond")
    
    agent.set_drivers([driver])

    drive = VLA_Star("navigate_in_water", driving_monitor, agent)

    asyncio.run(drive.run("Get to dock B."), exceptions=[VLA_StarInitializedException])

def smolvla():
    monitor = VLM("watcher", system_prompt="You are the perception system for a robotic arm. Take note of the status of the mission. Given the query, return either OK or a descriptive response. There is a cardboard box in the scene.")
    agent = GDA("decision-maker", None, \
    "You are a decision-making agent in a network of LLMs that compose a physical agent. Reach the prompted goal by supplying adequate arguments to your functions.\n" \
    "You may choose ANY of the available tools.\n"\
    "You must call exactly ONE tool.\n"\
    "After calling one tool, stop all further reasoning.\n"\
    "Do not produce natural-language output. "\
    "Return immediately after the tool call.\n")

    vla = FineTunedSmolVLA()
    driver = VLA_Complex("use_robotic_arm", agent, monitor, vla, \
    "Use a model to perform the instruction. Only make one tool call. This model is a fine-tuned VLA post-trained on only one task. Your instruction is a language prompt. This model's capabilities are the following:\n" \
    "'Put the colored blocks in the cardboard box' | STOP (which stops the model)")

    agent.set_drivers([driver])

    drive = VLA_Star("lerobot_travaille", monitor, agent)
    print("System initialized")
    asyncio.run(drive.run("Please put the blocks in the box."))

def main():
    #street_and_crosswalks()
    #navigate_river()
    #follow_path_river()
    smolvla()
"""

if __name__ == "__main__":
    print(f"No longer compatible with main()")
