import sys
print(sys.path)

import shop
from experiments.logger import log

if __name__ == "__main__":
    """
    Initialize environment, if needed, here.
    """
    participant = sys.argv[1]

    vla_star = shop.instantiate_chatting_bot()
    vla_star.safe_start()
    

