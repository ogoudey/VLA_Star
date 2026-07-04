import http.client
import json
import os
import subprocess
import platform



from .manifest_manager import get_manifest
from network.common import send_dict_to_olimn

def get_agents():
    return get_manifest()

def describe_host():
    info = f"""\
{os.environ['USER']}@{platform.node()} on {platform.machine()}, {platform.system()}, {platform.release()}
    """
    return info

def get_linux_wifi():
    try:
        # -r flag returns only the SSID name
        return subprocess.check_output(["iwgetid", "-r"]).decode("utf-8").strip()
    except Exception:
        return None
    
def get_local_area_description():
    """Return a short description suitable for filling in a sentence."""
    try:
        import geocoder
    except ImportError:
        return "nonlocated"
    g = geocoder.ip('me')
    return f"{g.city}, {g.country} (Lat: {g.lat}, Lng: {g.lng})" if g.ok else "dislocated"

def update_host_on_vlanet():
    # Get agents
    agents = get_agents()

    # Get unique host data
    host_desc = describe_host()

    # Get LAN data
    lan_desc = get_linux_wifi()

    # Get LA data
    la = get_local_area_description()

    content = {
        "agents": agents,
        "host":host_desc,
        "lan": lan_desc,
        "la": la 
    }

    send_dict_to_olimn("host", content)
    