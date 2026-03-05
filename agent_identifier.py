import os
from pathlib import Path
import json

def write_identifier(agent_name):
    filename_of_list_of_hosted_agents = Path(os.home) / ".vla_stars"
    with open(filename_of_list_of_hosted_agents, "a") as f:
        j = json.loads(f)
        j.remove(agent_name)
        f.write(json.dump(j))
    print(f"Agent {agent_name} written to {filename_of_list_of_hosted_agents}")

def del_identifier(agent_name):
    filename_of_list_of_hosted_agents = Path(os.home) / ".vla_stars"
    with open(filename_of_list_of_hosted_agents) as f:
        j = json.loads(f)
        j.remove(agent_name)
        f.write(json.dump(j))
    print(f"Agent {agent_name} written to {filename_of_list_of_hosted_agents}")
        
if __name__ == "__main__:
    import sys
    try:
        del_identifier(sys.argv[2])
    except Exception:
        print("Needs argv[2]")
        sys.exit(1)
