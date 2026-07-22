from host import manifest_manager, vlanet_interface
from vla_star.vla_star import VLA_Star

import getpass
import socket

def host_address():
    """Gets the primary local IP address of this machine.

    Creates a dummy UDP connection to a non-routable address to determine
    the interface IP that would actually be used to connect out.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 10.255.255.255 doesn't need to be reachable; no packets are sent
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def user():
    """Returns the username of the current logged-in user."""
    return getpass.getuser()

class Host:
    @staticmethod
    def list_vla_star(vla_star: VLA_Star):
        manifest_manager.update_manifest(vla_star.name, new_status="active",  host=host_address(), user=user(), message=f"To activate {vla_star.name}, use an activator class 1. If {vla_star.name} is active, open up a textual chat terminal on PORT.")

    @staticmethod
    def sync_manifest():
        vlanet_interface.update_host_on_vlanet()

    @staticmethod
    def update_vla_star_on_list(vla_star: VLA_Star):
        manifest_manager.update_manifest(vla_star.name, new_status="inactive", host=host_address(), user=user())