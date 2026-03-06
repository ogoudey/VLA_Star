import os
from pathlib import Path
import json

FILE = Path.home() / ".vla_stars.json"


def _read_list():
    if not FILE.exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)


def _write_list(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


def write_identifier(agent_name):
    agents = _read_list()

    if agent_name not in agents:
        agents.append(agent_name)

    _write_list(agents)

    print(f"Agent {agent_name} written to {FILE}")


def del_identifier(agent_name):
    agents = _read_list()

    if agent_name in agents:
        agents.remove(agent_name)

    _write_list(agents)

    print(f"Agent {agent_name} removed from {FILE}")
        
if __name__ == "__main__":
    import sys
    try:
        del_identifier(sys.argv[2])
    except Exception:
        print("Needs argv[2]")
        sys.exit(1)
