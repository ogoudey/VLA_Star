import sys
import os
import shop
from experiments.logger import start_phase_log, stop_phase_log
from setproctitle import setproctitle

if __name__ == "__main__":
    try:
        os.environ["AGENT_LABEL"] = sys.argv[1]
    except Exception:
        os.environ["AGENT_LABEL"] = "default_unity_phase_robot_name"
    try:
        os.environ["PLAY_MODE"] = sys.argv[2].upper()
    except Exception:
        os.environ["PLAY_MODE"] = "FREE"
    try:
        os.environ["AGENCY_TYPE"] = sys.argv[3].upper()
    except Exception:
        os.environ["AGENCY_TYPE"] = "AUTO"
    try:
        os.environ["CONTEXT_TYPE"] = sys.argv[4].upper()
    except Exception:
        os.environ["CONTEXT_TYPE"] = "HIGHREFLEXIVITY"
    setproctitle("vla_unity")
    vla_star = shop.instantiate_unity_robot()
    vla_star.safe_start()