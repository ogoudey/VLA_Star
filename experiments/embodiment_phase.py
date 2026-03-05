import sys
import os
import shop


if __name__ == "__main__":
    os.environ["AGENT_LABEL"] = f"dev_bot"
    vla_star = shop.instantiate_chatting_bot()
    vla_star.safe_start()
    

    
    

