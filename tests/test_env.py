import pytest

def test_import_agents():
    import agents
    print(f"agents: {agents.__version__}")
