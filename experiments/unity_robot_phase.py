import sys
import os
import shop

from setproctitle import setproctitle

if __name__ == "__main__":
    setproctitle("VLA* Unity")
    vla_star = shop.instantiate_unity_robot()
    vla_star.safe_start()
    

    
    

