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
    setproctitle("vla_unity")
    vla_star = shop.instantiate_unity_robot()
    vla_star.safe_start()