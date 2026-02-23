import sys
import os
import shop
from likert_survey import Survey


if __name__ == "__main__":
    """
    Initialize environment, if needed, here.
    """
    participant = sys.argv[1]
    os.environ["AGENT_LABEL"] = f"{participant}_chatter"
    vla_star = shop.instantiate_chatting_bot()
    vla_star.safe_start()

    s = Survey(participant, __file__)
    s.phase_survey()
    

    
    

