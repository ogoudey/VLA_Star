import time
import sys
from pathlib import Path
parent_dir = Path(__file__).resolve().parent
sys.path.append(str(parent_dir.parent))

from vla_star.vla_complex.utilities.chat_core import Router, Conversation, SSHClient, EntryInterface, OutInterface, SecretManager
# PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests

def test_server():
    router = Router()
    ssh_client = SSHClient()
    interface = OutInterface(router, ssh_client)
    time.sleep(10)

def open_interface():
    router = Router()
    ssh_client = SSHClient()
    interface = OutInterface(router, ssh_client)
    return interface