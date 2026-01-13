# Standard imports #

import os
import importlib.util
import sys
from pathlib import Path
from typing import Any, List

import vla_star
import gda
import vla_complex
import vla
from vlm import VLM
from vla_star import VLA_Star
from vla_complex import VLA_Complex

from vla import VLA
from gda import GDA, DemoedLanguageModel
from vla_complex import Logger, Chat, DrawOnBlackboard

from configs import RobotConfig, AgencyConfig, VLAComplexConfig
from configs import RobotType, AgencyType, MonitorType, VLAType

#########################
#
#       Factory
#
#
#################33

robot = None
agency = None
vla_complexes = []
_vla_star = None

def produce_robot(cfg: RobotConfig):
    global robot
    match cfg.robot_type:
        case RobotType.KINOVA:
            robot = "This is a Kinova "
        case RobotType.NONE:
            robot = None
        case _:
            raise ValueError(f"Unsupported robot type: {cfg.robot_type}")
    return robot

def produce_agency(cfg: AgencyConfig):
    global agency
    match cfg.agency_type:
        case AgencyType.AUTO:
            agency = make_agent()
        case AgencyType.FIXED:
            agency = "with fixed (no) agency, "
        case AgencyType.DEMOED:
            agency = make_demoed_agent()   
        case _:
            raise ValueError(f"Unsupported agency type: {cfg.agency_type}")
    return agency

def produce_vla_complexes(cfgs: List[VLAComplexConfig]):
    global vla_complexes
    complexes = []
    for cfg in cfgs:
        vla_complex = None
        if cfg.monitor_types:
            for monitor_type in cfg.monitor_types:
                match monitor_type:
                    case MonitorType.CONDUCT_RECORDING:
                        vla_complex = "conducted and "
                    case _:
                        raise ValueError(f"Unsupported monitor type: {monitor_type}")
        match cfg.agency_type:
            case AgencyType.ARM_VR_DEMO:
                vla_complex = "demoed with vr "
            case AgencyType.PASS_THROUGH:
                vla_complex = None
            case AgencyType.FIXED:
                vla_complex = None
            case _:
                raise ValueError(f"Unsupported agency type: {cfg.agency_type}")
        match cfg.vla_type:
            case VLAType.TEXT:
                vla_complex = Chat()
            case VLAType.ACTUATION:
                vla_complex = "arm"
            case _:
                raise ValueError(f"Unsupported VLA type: {cfg.vla_type}")
        if cfg.recorded:
            vla_complex += " while being recorded"
        complexes.append(vla_complex)
    vla_complexes = complexes
    return vla_complexes

def produce_vla_star():
    global robot
    global agency
    global vla_complexes
    global _vla_star
    try:
        _vla_star = VLA_Star(agency, vla_complexes)
        return _vla_star
    except Exception as e:
        raise Exception(f"Cannot produce VLA*. {e}.")

def get_vla_star():
    try:
        return _vla_star
    except Exception as e:
        raise Exception(f"Cannot return VLA*. Missing call to factory.produce_vla_star()")
    
#########3 Helpers ###########
def make_agent() -> GDA:
    return GDA("name_for_traces", \
    "You are a decision-making agent in a network of LLMs that compose a physical agent. Respond appropriately to the context by supplying adequate arguments to a function.\n" \
    "You may choose ANY of the available tools.\n"\
    "You must call only ONE tool. Your job is to efficiently call that single tool.\n"\
    "After calling a SINGLE tool, stop all further reasoning.\n"\
    "Do not produce natural-language final output. "\
    "Return immediately after the ONE tool call.\n"\
    "Use the blackboard to do any and all planning, like a 'behavior tree' might, but still, as for every tool call, return immediately after.\n")

def make_demoed_agent():
    return DemoedLanguageModel()

"""
def get_real_vision(override_values=[]):
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

        m.vision = image_processors
        m.reflex_vision = m.vision[:2]
        m.command_vision = m.vision[0]
        
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
    def create(demo_language_model=False, use_text=False):
        Factory.common()
        ### ====== Morphology ===== ###

        # It's just an assumed object at the end of a socket.
        os.environ["WAYPOINTS"] = "5000"
        os.environ["TERRAIN"] = "5003"

        # === Brains === #
        from pathlib import Path
        import sys
        path_planning_path = os.environ.get("PATH_PLANNING", "/home/olin/Robotics/AI Planning/Path-Planning")
        sys.path.append(path_planning_path)
        if not Path(path_planning_path).exists():
            raise FactoryException("Failed to import Path Planning.")
        else:
            print("Importing Path Planning")
            import space
            import math

        planner = vla.PathFollow()

        from vla_complex import Navigator
        vla_complexes:List[Any] = [
            Navigator(planner, \
    f"Use to move robot (sailboat) to desired location. Only call this when you're sure you want to start a journey to the destination. Only call this tool once. The destinations are the following (choose one BY EXACT NAME to pass as an argument):\n" \
    f"destination: {planner.destinations} | STOP (which stops the model)", "go_to_destination")
        ]
        if use_text:
            vla_complexes.append(DrawOnBlackboard())
            vla_complexes.append(Logger())
            vla_complexes.append(Chat())

        if demo_language_model:
            gda = DemoedLanguageModel(
                "To respond adequately."
            )
        else:
            gda = GDA("name_for_traces", \
    "You are a decision-making agent in a network of LLMs that compose a physical agent. Reach the prompted goal by supplying adequate arguments to your functions.\n" \
    "You may choose ANY of the available tools.\n"\
    "You must call exactly ONE tool (unless logging).\n"\
    "After calling one tool (except log), stop all further reasoning.\n"\
    "Do not produce natural-language final_output. "\
    "It is recommended to use the `draw_on_blackboard` function when you want to make a plan that persists across agents.\n")
        return VLA_Star(gda, vla_complexes)


class SO101_Recorder_VLA_Star_Factory(Factory):
    requirements={"modules":"vla_interface"}
    @staticmethod
    def create():
        Factory.common()
        ### ====== Morphology ===== ###

        m = Morphology()
        
        ### REAL LOCATION ###
        
        
        custom_brains = Path(os.environ.get("LEROBOT", "/home/mulip-guest/LeRobot/lerobot/custom_brains")) #import editable lerobot for VLA
        sys.path.append(custom_brains.as_posix())
        print(sys.path)
        if not custom_brains.exists():
            print("No SmolVLA")
            raise FactoryException(f"Could not add {custom_brains} to sys.path")
        try:
            import vla_interface # should be robot-isolated
        except Exception as e:
            print(e)
            raise FactoryException("Failed to import LeRobot etc.")
        m.body = vla_interface.create_body() # should be something like my_robot.create()
        
        image_processors = get_real_vision()

        m.vision = image_processors
        m.reflex_vision = m.eyes[:2]

        ### ===== Brains ====== ###
        
        ### VIRTUAL LOCATION for action recorder ###
        
        custom_brains = Path(os.environ.get("LEROBOT", "/home/mulip-guest/LeRobot/lerobot/custom_brains"))#import editable lerobot for VLA
        sys.path.append(custom_brains.as_posix())
        if not custom_brains.exists():
            print("No SmolVLA")
            raise FactoryException(f"Could not add {custom_brains} to sys.path")
        try:
            import vla_interface
        except Exception as e:
            print(e)
            raise FactoryException("Failed to import LeRobot etc.")
         
        ### Initialize action recorder (vla)
        import datetime
        dr = vla_interface.create_teleop_recording_interaction(
            reader_assignments={
                "side": m.vision[0],
                "up": m.vision[1],
            },
            dataset_name=f"LLM_VLA_demo_{datetime.datetime.now()}"
        )
        recorder_caller = vla.DatasetRecorderCaller(dr)
        
        ### Initialize GDA (LLM) ###
        input("Ready to demo the instructions?")
        inputter = DemoedLanguageModel()
        
        vlm_like = None # pass - is demoed

        ### Initialize VLA Complexes ###
        from vla_complex import EpisodicRecorder
        ### GDA >> VLM Perception >> VLA ###
        vla_complexes = [
            EpisodicRecorder(recorder_caller, "record_wrapper")
        ]
    
        return VLA_Star(inputter, vla_complexes)



class Mock_VLA_Star_Text(Factory):
    @staticmethod
    def create(demo_language=False):
        
        Factory.common()
        ### ====== Morphology ===== ###

        m = Morphology()

        inputter = DemoedLanguageModel()

        inputter = make_agent()
        vla_complexes = [
            Logger(),
            Chat(),
            DrawOnBlackboard()
        ]
    
        return VLA_Star(inputter, vla_complexes)

class Mock_Recorder_VLA_Star_Factory(Factory):
    @staticmethod
    def create():
        Factory.common()
        ### ====== Morphology ===== ###

        m = Morphology()
        
        ### REAL LOCATION ###
        
        
        custom_brains = Path(os.environ.get("LEROBOT", "/home/mulip-guest/LeRobot/lerobot/custom_brains")) #import editable lerobot for VLA
        sys.path.append(custom_brains.as_posix())
        if not custom_brains.exists():
            print("No SmolVLA")
            raise FactoryException(f"Could not add {custom_brains} to sys.path")
        try:
            import vla_interface # should be robot-isolated
        except Exception as e:
            print(e)
            raise FactoryException("Failed to import LeRobot etc.")
        
        # No body

        # No vision

        ### ===== Brains ====== ###
        
        ### VIRTUAL LOCATION for action recorder ###

        ### Initialize action recorder (vla)
        import datetime
        dr = vla_interface.create_unrecorded_mock_interaction(
            dataset_name=f"MOCK_LLM_VLA_demo_{datetime.datetime.now()}"
        )
        recorder_caller = vla.DatasetRecorderCaller(dr)

        ### Initialize GDA (LLM) ###
        lm = DemoedLanguageModel()
        
        vlm_like = None # pass - is demoed

        ### Initialize VLA Complexes ###
        from vla_complex import EpisodicRecorder

        vla_complexes = [
            EpisodicRecorder(recorder_caller, "record_wrapper")
        ]
    
        return VLA_Star(lm, vla_complexes)


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
    #vla_star_1 = SmolVLA_S0101_VLA_Star_Factory.create()
    #vla_star_1.run()
    b=PathPlanner_VLAStar_Factory.create(True, True)
    b.run("go to Well Island, then Bear Island")
"""