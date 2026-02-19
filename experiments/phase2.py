import sys
import os
import shop
from experiments.logger import log

if __name__ == "__main__":
    """
    Initialize environment, if needed, here.
    """
    participant = sys.argv[1]
    os.environ["AGENT_LABEL"] = f"{participant}_chatter2"

    vla_star = shop.instantiate_chatting_bot()
    vla_star.safe_start()
    
    groundedness = input("Did A or B feel more grounded?")
    log(__file__, {
        "participant": participant,
        "groundedness": groundedness
    })

    
