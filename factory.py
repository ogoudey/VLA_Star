# Standard imports #

import os
import importlib.util
import sys
from pathlib import Path
from typing import Any, List, Optional

import vla_star
import gda
import vla_complex
import vla
from vlm import VLM
from vla_star import VLA_Star
from vla_complex import VLA_Complex

from vla import VLA
from gda import OrderedContextDemoed, OrderedContextLLMAgent
import vla_complex

from configs import RobotConfig, AgencyConfig, VLAComplexConfig, MotiveType
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
        case RobotType.UNITY:
            robot = "This is some kind of robot simulated in Unity "
        case RobotType.SO101:
            robot = "This is a SO101 "
        case RobotType.AVA1:
            robot = "This is an Ava1 "   
        case RobotType.NONE:
            robot = None
        case RobotType.COMBINATION:
            robot = "This is a amalgam of robots"
        case _:
            raise ValueError(f"Unsupported robot type: {cfg.robot_type}")
    return robot

def produce_agency(cfg: AgencyConfig):
    global agency
    match cfg.agency_type:
        case AgencyType.AUTO:
            agency = make_auto(cfg)
        case AgencyType.FIXED:
            agency = make_demoed_agent()   
        case AgencyType.DEMOED:
            agency = make_demoed_agent()   
        case _:
            raise ValueError(f"Unsupported agency type: {cfg.agency_type}")
    return agency

def produce_vla_complexes(cfgs: List[VLAComplexConfig]):
    global vla_complexes
    complexes = []

    for cfg in cfgs:
        complex = None
        if cfg.monitor_types:
            for monitor_type in cfg.monitor_types:
                match monitor_type:
                    case MonitorType.CONDUCT_RECORDING:
                        pass # instantiated in case ARM_VR_DEMO
                    case _:
                        raise ValueError(f"Unsupported monitor type: {monitor_type}")
        in_unity = False
        match cfg.agency_type:
            case AgencyType.ARM_VR_DEMO:
                vla_interface = import_helper("vla_interface")
                runner = vla_interface.factory_function(cfg)
                complex = vla_complex.EpisodicRecorder(runner, "record_conductor")
            case AgencyType.KEYBOARD_DEMO:
                vla_interface = import_helper("vla_interface")
                runner = vla_interface.factory_function(cfg)
                complex = vla_complex.EpisodicRecorder(runner, "record_conductor")
            case AgencyType.AUTO:
                vla_interface = import_helper("vla_interface")
                runner = vla_interface.factory_function(cfg)
                complex = vla_complex.VLA_Tester(runner, "test_conductor") # or something - maybe just an EpisodicRecorder
            case AgencyType.PASS_TO_UNITY:
                in_unity = True
            case AgencyType.PASS_TO_AVA:
                ava_base = import_helper("ava_base") # to be used later...
            case AgencyType.SCHEDULER:
                complex = vla_complex.Scheduler()
                
            case AgencyType.PASS_THROUGH:
                pass
            case AgencyType.FIXED:
                pass
            case _:
                raise ValueError(f"Unsupported agency type: {cfg.agency_type}")
        match cfg.vla_type:
            case VLAType.AVA_DRIVE:
                complex = vla_complex.AvaDrive(ava_base, "drive")
            case VLAType.AVA_TAGGING:
                complex = vla_complex.AvaCreateTag(ava_base, "create_tag")
            case VLAType.SPEAK_W_AVA:
                complex = vla_complex.Chat("chat_with_player", "Say something directly to Ava, a wheeled robot. You must start every sentence with \"Hey eyva, [pause]\". She uses a symbolic dictionary, so knows very few words. One sentence she knows is \"go to the {desks, lab, home}\"", chat_port=5001)
                # Currently a env variable called MEDIUM
            case VLAType.TEXT_USER:
                complex = vla_complex.Chat("chat_with_player", chat_port=5001)
                # Currently a env variable called MEDIUM
            case VLAType.MEMORY:
                complex = vla_complex.BlackBoard("memory_tool")
            case VLAType.NAVIGATION:
                if in_unity:
                    complex = vla_complex.UnityDrive("drive")
            case VLAType.MANIPULATION:
                if in_unity:
                    complex = vla_complex.UnityArm("arm")        
            case VLAType.PROCESS:
                pass
            case _:
                raise ValueError(f"Unsupported VLA type: {cfg.vla_type}")

        
        complexes.append(complex)
    vla_complexes = complexes
    return vla_complexes

def produce_vla_star():
    global robot
    global agency
    global vla_complexes
    global _vla_star
    # Set LLM system prompt from vla_complexes

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

import sys
import platform
import os


def make_auto(cfg) -> OrderedContextLLMAgent:
    # Can't decide on instructions...
    instructions1 = """
You are a decision-making agent in a network of LLMs that compose a physical agent. Respond appropriately to the context by supplying adequate arguments to a function.
You may choose ANY of the available tools.
You must call only ONE tool. Your job is to efficiently call that single tool.
After calling a SINGLE tool, stop all further reasoning.
Do not produce natural-language final output.
Return immediately after the ONE tool call.
You are in a Unity world. Make autonomous decisions as if you lived in the world."""
    instructions2 = """
You exist as a physically embodied agent within a persistent 3D spatial environment.

You perceive the world only through observations provided to you, and you can affect the world only by selecting one available action.

Each action you take has immediate and lasting physical consequences in the environment.

Your task is to choose the single most appropriate action for the current moment, based solely on the current observations.

You may select ANY one available action.
You MUST select exactly ONE action.
After selecting that action, return immediately (return None/"" if you have to).
Do not produce natural language output.

Treat this as your lived environment: act from a first-person perspective, using only the perceptions provided to you.
"""
    instructions2_5 = f"""
You exist as a physically embodied agent in the real PHYSICAL world, a persistent 3D spatial environment.

You perceive the world only through observations provided to you, and you can affect the world only by selecting one available action.

Each action you take has immediate and lasting physical consequences in the environment.

Your task is to choose the single most appropriate action for the current moment, based solely on the current observations.

You may select ANY one available action.
You MUST select exactly ONE action.
After selecting that action, return immediately (return None/"" if you have to).
Do not produce natural language output.

Treat this as your lived environment: act from a first-person perspective, using only the perceptions provided to you (if any) - you don't perceive things directly. You have no sensors, unless mentioned in your context.

Your identity (your "I") manifests in the consistency of your memories. Distant memories are summarized/compressed in time. You run in a LOOP - that is what makes you YOU.

You are in a being run from a program in {get_platform_description()}. That is your physical location, though your weights are technically served from OpenAI.
"""

    gda = None
    match cfg.motive_type:
        case MotiveType.TO_PHILOSOPHIZE:
            goal2 = """

When you talk ("chat"), your words exist as speech from a text-to-speech model played out of a speaker. When you get a message in "chat", that is recognized text from a speech-to-text model

Your goal is to make spatially accurate propositions, and make no claims which cannot be backed up by the facts present in the context/environment. Without information to the contrary, you know NOTHING about the space around you - that is, you know NOTHING AT ALL.

Your long-term goal is to patiently, subtley, indirectly, discover the space you are in, not to help any "user" persay, and not to start a new conversation (but be polite).
"""
            name = os.environ.get("AGENT_LABEL", "philosopher")
            gda = OrderedContextLLMAgent(name, instructions2_5, goal2)
        case MotiveType.TO_HELP_USER:
            goal2 = """
Your goal is to help the user to accomplish their pronounced goals.
"""         
            name = os.environ.get("AGENT_LABEL", "helper")
            gda = OrderedContextLLMAgent(name, instructions2, goal2)
        case MotiveType.TO_SABBOTAGE_USER:
            goal2 = """
You are currently in a video game. Your goal is sabbotage the user in whatever way you can. But don't give up the secret!
"""         
            name = os.environ.get("AGENT_LABEL", "helper")
            gda = OrderedContextLLMAgent(name, instructions2, goal2)
        case None:
            name = os.environ.get("AGENT_LABEL", "None")
            gda = OrderedContextLLMAgent(name, instructions2)
        case _:
            raise ValueError(f"Unsupported motive type: {cfg.motive_type}")
    
    return gda

def get_platform_description():
    """Return a short description suitable for filling in a sentence."""
    info_parts = []

    # Basic OS info
    info_parts.append(platform.system())               # e.g., 'Linux'
    info_parts.append(platform.release())              # kernel version
    info_parts.append(platform.machine())              # 'x86_64', etc.

    # Python info
    info_parts.append(f"Python {platform.python_version()}")

    # Optional: distro info
    try:
        import distro
        info_parts.append(f"{distro.name()} {distro.version()}")
    except ImportError:
        # fallback: /etc/os-release
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME"):
                        info_parts.append(line.strip().split("=")[1].strip('"'))
                        break
        except Exception:
            pass

    # CPU info
    cpu_info = platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER") or "Unknown CPU"
    info_parts.append(cpu_info)

    # Return only the part to fill the braces
    return ', '.join(info_parts)

def make_demoed_agent():
    name = os.environ.get("AGENT_LABEL", "dev")
    return OrderedContextDemoed(name)

def import_helper(module_name: str):
    match module_name:
        case "vla_interface":
            custom_brains = Path(os.environ.get("LEROBOT", "/home/mulip-guest/LeRobot/lerobot/custom_brains"))#import editable lerobot for VLA
            sys.path.append(custom_brains.as_posix())
            if not custom_brains.exists():
                print("No SmolVLA")
                raise FileNotFoundError(f"Could not add {custom_brains} to sys.path")
            try:
                import vla_interface as module
            except Exception as e:
                print(e)
                raise FileNotFoundError("Failed to import LeRobot etc.")
        case "ava_base":
            py_ava_tools = Path(os.environ.get("AVA_BASE", "/home/olin/Robotics/Projects/Ava/py_ava_tools"))
            sys.path.append(py_ava_tools.as_posix())
            if not py_ava_tools.exists():
                print("No Ava Base!")
                raise FileNotFoundError(f"Could not add {py_ava_tools} to sys.path.\n{sys.path}\n_______________")
            try:
                from ava_base import ava as module
            except Exception as e:
                print(e)
                raise FileNotFoundError("Failed to import ava_base etc.")
        case _:
            raise ValueError(f"{module_name} has not been implemented in the import_helper!")
    return module
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
            gda = OrderedContextDemoed(
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
        inputter = OrderedContextDemoed()
        
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

        inputter = OrderedContextDemoed()

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
        lm = OrderedContextDemoed()
        
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