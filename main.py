import factory

from configs import RobotConfig, AgencyConfig, VLAComplexConfig
from configs import RobotType, AgencyType, MonitorType, VLAType, MotiveType

def instantiate_ava():
    robot_cfg = RobotConfig(
        robot_type = RobotType.AVA1
    )
    factory.produce_robot(robot_cfg)
    agency_cfg = AgencyConfig(
        agency_type = AgencyType.AUTO,
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
        agency_type = AgencyType.AUTO,
        recorded = False,
        motive_type = MotiveType.TO_HELP_USER
    )

    factory.produce_agency(agency_cfg)

    vla_complex_cfgs = [
        VLAComplexConfig(
            vla_type = VLAType.ACTUATION,
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
        agency_type = AgencyType.AUTO,
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
    ]

    factory.produce_vla_complexes(vla_complex_cfgs)

    factory.produce_vla_star()

    return factory.get_vla_star()

if __name__ == "__main__":
    v = instantiate_unity_robot()
    v.start()


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
        agency_type = AgencyType.ARM_VR_DEMO,
        monitor_types = [
            MonitorType.CONDUCT_RECORDING
        ],
        recorded = True
    ),
]

factory.produce_vla_complexes(vla_complex_cfgs)

x = factory.produce_vla_star()
print(x)



"""