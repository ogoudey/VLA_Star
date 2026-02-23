import factory
from pathlib import Path    # For adjustable policy paths
import os
from configs import RobotConfig, AgencyConfig, VLAComplexConfig
from configs import RobotType, AgencyType, MonitorType, VLAType, MotiveType

def instantiate_so101_ava():
    robot_cfg = RobotConfig(
        robot_type = RobotType.COMBINATION
    )
    factory.produce_robot(robot_cfg)
    agency_cfg = AgencyConfig(
        agency_type = AgencyType.DEMOED,
        recorded = False
    )
    factory.produce_agency(agency_cfg)
    vla_complex_cfgs = [
        VLAComplexConfig(
            vla_type = VLAType.MANIPULATION,  # -- 
            agency_type = AgencyType.AUTO, # _/
            robot_type = RobotType.SO101,
            #dataset_name = "test1_dataset",
            policy_path = Path("/home/olin/Robotics/Projects/VLA_Star/021000/pretrained_model"),
            monitor_types = [],
            recorded = False
        ),
        VLAComplexConfig(
            vla_type = VLAType.TEXT_USER,
            agency_type = AgencyType.PASS_THROUGH,
            monitor_types = [],
            recorded = False
        ),
        VLAComplexConfig(
            vla_type = VLAType.AVA_DRIVE,
            agency_type = AgencyType.PASS_TO_AVA,
            monitor_types = [],
            recorded = False
        )
    ]
    factory.produce_vla_complexes(vla_complex_cfgs)
    factory.produce_vla_star()
    return factory.get_vla_star()

def instantiate_so101_tester():
    robot_cfg = RobotConfig(
        robot_type = RobotType.SO101
    )
    factory.produce_robot(robot_cfg)
    agency_cfg = AgencyConfig(
        agency_type = AgencyType.AUTO,
        recorded = False
    )
    factory.produce_agency(agency_cfg)
    vla_complex_cfgs = [
        VLAComplexConfig(
            vla_type = VLAType.MANIPULATION,  # -- 
            agency_type = AgencyType.AUTO, # _/
            robot_type = RobotType.SO101,
            policy_path = Path("path_to_testable_policy"),
            monitor_types = [], # just to test, monitors are ex-
            recorded = False
        ),
        VLAComplexConfig(
            vla_type = VLAType.TEXT_USER,
            agency_type = AgencyType.PASS_THROUGH,
            monitor_types = [],
            recorded = False
        ),
    ]
    factory.produce_vla_complexes(vla_complex_cfgs)
    factory.produce_vla_star()
    return factory.get_vla_star()

def instantiate_ava():
    """
    Ava WIFI + base connections do not work together, so cannot have AgencyType.AUTO + AVA_DRIVE
    """
    robot_cfg = RobotConfig(
        robot_type = RobotType.AVA1
    )
    factory.produce_robot(robot_cfg)
    agency_cfg = AgencyConfig(
        agency_type = AgencyType.DEMOED,
        recorded = False
    )
    factory.produce_agency(agency_cfg)
    vla_complex_cfgs = [
        VLAComplexConfig(
            vla_type = VLAType.AVA_DRIVE,
            agency_type = AgencyType.PASS_TO_AVA,
            monitor_types = [],
            recorded = False
        ),
        VLAComplexConfig(
            vla_type = VLAType.TEXT_USER,
            agency_type = AgencyType.PASS_THROUGH,
            monitor_types = [],
            recorded = False
        ),
    ]
    factory.produce_vla_complexes(vla_complex_cfgs)
    factory.produce_vla_star()
    return factory.get_vla_star()

def instantiate_ava_tagger():
    robot_cfg = RobotConfig(
        robot_type = RobotType.AVA1
    )
    factory.produce_robot(robot_cfg)
    agency_cfg = AgencyConfig(
        agency_type = AgencyType.DEMOED,
        recorded = False
    )
    factory.produce_agency(agency_cfg)
    vla_complex_cfgs = [
        VLAComplexConfig(
            vla_type = VLAType.AVA_DRIVE,
            agency_type = AgencyType.PASS_TO_AVA,
            monitor_types = [],
            recorded = False
        ),
        VLAComplexConfig(
            vla_type = VLAType.AVA_TAGGING,
            agency_type = AgencyType.PASS_TO_AVA,
            monitor_types = [],
            recorded = False
        ),
        VLAComplexConfig(
            vla_type = VLAType.TEXT_USER,
            agency_type = AgencyType.PASS_THROUGH,
            monitor_types = [],
            recorded = False
        ),
    ]
    factory.produce_vla_complexes(vla_complex_cfgs)
    factory.produce_vla_star()
    return factory.get_vla_star()

def instantiate_unity_robot():
    robot_cfg = RobotConfig(
        robot_type = RobotType.UNITY
    )
    factory.produce_robot(robot_cfg)

    agency_cfg = AgencyConfig(
        agency_type = AgencyType.DEMOED,
        recorded = False,
        motive_type = MotiveType.TO_HELP_USER
    )

    factory.produce_agency(agency_cfg)

    vla_complex_cfgs = [
        VLAComplexConfig(
            vla_type = VLAType.NAVIGATION,
            agency_type = AgencyType.PASS_TO_UNITY,
            monitor_types = [
                MonitorType.CONDUCT_RECORDING
            ],
            recorded = False
        ),
        VLAComplexConfig(
            vla_type = VLAType.MANIPULATION,
            agency_type = AgencyType.PASS_TO_UNITY,
            monitor_types = [
                MonitorType.CONDUCT_RECORDING
            ],
            recorded = False
        ),
        VLAComplexConfig(
            vla_type = VLAType.TEXT_USER,
            agency_type = AgencyType.PASS_THROUGH,
            monitor_types = [],
            recorded = False
        ),
        VLAComplexConfig(
            vla_type = VLAType.PROCESS,
            agency_type = AgencyType.SCHEDULER,
            monitor_types = [],
        )
    ]

    factory.produce_vla_complexes(vla_complex_cfgs)

    factory.produce_vla_star()
    
    return factory.get_vla_star()

def instantiate_vla_kinova_training():
    """
    This is a Kinova with fixed (no) agency, and ['a conducted and demoed with vr arm while being recorded']
    """
    robot_cfg = RobotConfig(
        robot_type = RobotType.KINOVA
    )
    factory.produce_robot(robot_cfg)

    agency_cfg = AgencyConfig(
        agency_type = AgencyType.FIXED,
        recorded = False
    )

    factory.produce_agency(agency_cfg)

    vla_complex_cfgs = [
        VLAComplexConfig(
            vla_type = VLAType.ACTUATION,
            agency_type = AgencyType.ARM_VR_DEMO,
            monitor_types = [
                MonitorType.CONDUCT_RECORDING
            ],
            recorded = True
        ),
    ]

    factory.produce_vla_complexes(vla_complex_cfgs)

    factory.produce_vla_star()
    
    return factory.get_vla_star()

def instantiate_chatting_bot():
    """
    This is a non-robot with demonstrated agency, and ['a default chat interface']
    """
    robot_cfg = RobotConfig(
        robot_type = RobotType.NONE
    )
    factory.produce_robot(robot_cfg)

    agency_cfg = AgencyConfig(
        agency_type = AgencyType.DEMOED,
        motive_type=MotiveType.TO_PHILOSOPHIZE,
        recorded = False
    )

    factory.produce_agency(agency_cfg)
    vla_complex_cfgs = [
        VLAComplexConfig(
            vla_type = VLAType.TEXT_USER,
            agency_type = AgencyType.PASS_THROUGH,
            monitor_types = [],
            recorded = False
        ),
        VLAComplexConfig(
            vla_type = VLAType.MEMORY,
            agency_type = AgencyType.PASS_THROUGH,
            monitor_types = [],
            recorded = False
        )
    ]

    factory.produce_vla_complexes(vla_complex_cfgs)

    factory.produce_vla_star()

    return factory.get_vla_star()

if __name__ == "__main__":
    v = instantiate_unity_robot()
    v.start()