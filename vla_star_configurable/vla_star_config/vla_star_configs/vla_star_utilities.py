import uuid

def generate_unique_name():
    _uuid = uuid.uuid4()
    return f"agent_named_{str(_uuid)[4:]}"