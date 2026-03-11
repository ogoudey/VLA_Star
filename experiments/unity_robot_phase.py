import sys
import os
import shop

from setproctitle import setproctitle

if __name__ == "__main__":
    setproctitle("vla_unity")
    vla_star = shop.instantiate_unity_robot()
    vla_star.safe_start()