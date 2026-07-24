import time
import sys
from pathlib import Path
import getpass
parent_dir = Path(__file__).resolve().parent
sys.path.append(str(parent_dir.parent))

from vla_star.vla_complex.utilities.chat_core import Router, Conversation, SSHClient, EntryInterface, OutInterface, SecretManager, LocalNetworkManager
# PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests

def test_ssh_password_for_localhost():
    assert SecretManager.get_ssh_password_for_host_and_user("xps", "olin") == input("Check that your own password is in .secrets: ")

def test_this_host_manifest():
    print(f"===================== Manifest begin ==================\n\n{LocalNetworkManager._get_local_manifests_from_file()}\n\n===================== Manifest end ==================")

def test_local_agents():
    print(f"===================== Local agents begin ==================\n\n{LocalNetworkManager.get_local_agents()}\n\n===================== Local agents end ==================")

