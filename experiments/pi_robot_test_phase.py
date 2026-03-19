import sys
import os
import shop

from setproctitle import setproctitle

if __name__ == "__main__":
    setproctitle("VLA*")
    vla_star = shop.instantiate_chatting_bot()
    vla_star.safe_start()
    

    
    

