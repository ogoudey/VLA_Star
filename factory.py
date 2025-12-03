# Standard imports #

import os
import importlib.util
import sys
from pathlib import Path

import vla_star
import gda
import vla_complex
import vla
from vlm import VLM
from vla_star import VLA_Star
from vla_complex import VLA_Complex

from vla import VLA
from gda import GDA

class Factory:
    @classmethod
    def test(cls, verbose=False):
        if not hasattr(cls, "create"):
            return False
        if hasattr(cls, "requirements"):
            if "modules" in cls.requirements:
                for m in cls.requirements["modules"]:
                    if not Factory.module_exists(m):
                        if verbose:
                            print(f"{m} is required to create this")
                        return False
        return True
        
    @staticmethod  
    def module_exists(name):
        return importlib.util.find_spec(name) is not None
    
    @staticmethod
    def common():
        try:
            # shouldnt do imports here... scope problem...
            pass
            
        except Exception as e:
            print(f"Could not import vla_star: {e}")
            raise FactoryException(f"Could not import vla_star: {e}")


class LLM:
    pass

class CloudLLM(LLM):
    pass

class FactoryException(Exception):
    pass

class Morphology:
    pass

class BlindLeader(Factory):
    pass
    @staticmethod
    def create():
        Factory.common()
        blind_person = Morphology()
        image_processors = get_real_eyes()

        blind_person.eyes = image_processors

        policy = "act_blind_with_info_from_vlms"

        ### CLOUD LOCATION for llm and vlm ###
        if "OPENAI_API_KEY" in os.environ:
            pass
        else:
            # look for local models?
            raise FactoryException("Could not find OPENAI_API_KEY environment variable.")
        # no backup
        
        ### Initialize watcher
        vlm_guide = VLM("guide", "o4-mini", system_prompt="You are a visual system for a blind person. Help them to function by responding to their queries and providing necessary status updates.",\
                          recommendation_system_prompt="You are a visual system for a blind person. Help them to function by guiding their movement in a world they cannot see directly.")
        
        gda = None # the person makes the decisions 

        ### Initialize VLA Complexes ###
        from vla_complex import AnnounceIntent

        pass

def get_real_eyes():
    try:
        import image_processors as v
        image_processors = v.create(values=[2,4])
    except Exception:
        try:
            image_processors = v.create(values=["url1", "url2"])
        except Exception:
            raise FactoryException("Could not create any eyes.")
    return image_processors

class SmolVLA_S0101_VLA_Star_Factory(Factory):
    requirements={"modules":"vla_interface"}
    @staticmethod
    def create():
        Factory.common()
        ### ====== Morphology ===== ###

        m = Morphology()
        
        ### REAL LOCATION ###
        image_processors = get_real_vision()

        m.eyes = image_processors
        m.reflex_eye = m.eyes[:2]
        m.command_eye = m.eyes[0]
        
        ### Initializing morphology (awaiting better arrangement of LeRobot to distinguish physical/brains) ### 
        custom_brains = Path("/home/mulip-guest/LeRobot/lerobot/custom_brains")#import editable lerobot for VLA
        sys.path.append(custom_brains.as_posix())
        if not custom_brains.exists():
            print("No SmolVLA")
            raise FactoryException("Could not add /home/mulip-guest/LeRobot/lerobot/custom_brains to sys.path")
        try:
            import vla_interface # should be robot-isolated
        except Exception as e:
            print(e)
            raise FactoryException("Failed to import LeRobot etc.")
        m.body = vla_interface.create_body() # should be something like my_robot.create()
        
        ### ===== Brains ====== ###
        
        ### VIRTUAL LOCATION for vla ###
        
        custom_brains = Path("/home/mulip-guest/LeRobot/lerobot/custom_brains")#import editable lerobot for VLA
        sys.path.append(custom_brains.as_posix())
        if not custom_brains.exists():
            print("No SmolVLA")
            raise FactoryException("Could not add /home/mulip-guest/LeRobot/lerobot/custom_brains to sys.path")
        try:
            import vla_interface
        except Exception as e:
            print(e)
            raise FactoryException("Failed to import LeRobot etc.")
         
        ### Initialize vla
        smolvla_blocks_box_rdy = vla_interface.create_brains(
            reader_assignments={
                "side": m.reflex_eyes[0],
                "up": m.reflex_eyes[1]
            },
            policy_path=Path("/home/mulip-guest/LeRobot/lerobot/outputs/blocks_box/checkpoints/021000/pretrained_model")
        )
        smolvla_blocks_box = vla.SmolVLACaller(smolvla_blocks_box_rdy) # will initialize vla, and take a second
        
        ### CLOUD LOCATION for llm and vlm ###
        if "OPENAI_API_KEY" in os.environ:
            pass
        else:
            # look for local models?
            raise FactoryException("Could not find OPENAI_API_KEY environment variable.")
        # no backup
        
        ### Initialize watcher
        vlm_watcher = VLM("watcher", "o4-mini", system_prompt="You are the perception system for a robotic arm. Take note of the status of the mission. Given the query, return either OK or a descriptive response. There is a cardboard box in the scene.") # defaults to OPENAI
        
        ### Initialize GDA (LLM) ###
        gda = GDA("name_for_traces", \
    "You are a decision-making agent in a network of LLMs that compose a physical agent. Reach the prompted goal by supplying adequate arguments to your functions.\n" \
    "You may choose ANY of the available tools.\n"\
    "You must call exactly ONE tool.\n"\
    "After calling one tool, stop all further reasoning.\n"\
    "Do not produce natural-language output. "\
    "Return immediately after the tool call.\n") #Removed "drivers" argument
        
        ### Initialize VLA Complexes ###
        from vla_complex import Single_VLA_w_Watcher
        ### GDA >> VLM Perception >> VLA ###
        vla_complexes = [
            Single_VLA_w_Watcher(smolvla_blocks_box, vlm_watcher,   \
    "Use a model to perform the instruction. Only make one tool call. This model is a fine-tuned VLA post-trained on only one task. Your instruction is a language prompt. This model's capabilities are the following:\n" \
    "'Put the colored blocks in the cardboard box' | STOP (which stops the model)", "use_robotic_arm", )
        ]
    
        return VLA_Star(gda, vla_complexes)

class PathPlanner_VLAStar_Factory(Factory):

    @staticmethod
    def create():
        Factory.common()
        ### ====== Morphology ===== ###

        # It's just an assumed object at the end of a socket.
        os.environ["WAYPOINTS"] = "5000"
        os.environ["TERRAIN"] = "5003"

        # === Brains === #
        from pathlib import Path
        import sys
        sys.path.append("/home/olin/Robotics/AI Planning/Path-Planning")
        if not Path("/home/olin/Robotics/AI Planning/Path-Planning").exists():
            raise FactoryException("Failed to import Path Planning.")
        else:
            print("Importing Path Planning")
            import space
            import math

        planner = vla.PathFollow()

        from vla_complex import Navigator
        vla_complexes = [
            Navigator(planner, \
    f"Use to move robot (sailboat) to desired location. Only make one tool call. The destinations are the following (choose one BY EXACT NAME to pass as an argument):\n" \
    f"{planner.destinations} | STOP (which stops the model)", "go_to_destination")
        ]
        gda = GDA("name_for_traces", \
    "You are a decision-making agent in a network of LLMs that compose a physical agent. Reach the prompted goal by supplying adequate arguments to your functions.\n" \
    "You may choose ANY of the available tools.\n"\
    "You must call exactly ONE tool.\n"\
    "After calling one tool, stop all further reasoning.\n"\
    "Do not produce natural-language output. "\
    "Return immediately after the tool call.\n")
        return VLA_Star(gda, vla_complexes)


def test():
    compatible_classes = []
    for cls in Factory.__subclasses__():
        if cls.test():
            compatible_classes.append(cls)
    if len(compatible_classes) > 0:
        print("Compatible classes:")
        for cls in compatible_classes:
            print(f"\t{cls.__name__}")
    else:
        print("No compatible classes...")

if __name__ == "__main__":
    test()
    b = BlindLeader.create()
    #vla_star_1 = SmolVLA_S0101_VLA_Star_Factory.create()
    #vla_star_1.run()