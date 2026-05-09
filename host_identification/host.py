import http.client
import json
import os
import subprocess

"""
Hits API for UPDATE host
"""

from ..vla_star_factory.context_engine_factories.context_engine_factory_utilities import platform_description


OLIMN_API_KEY = os.environ.get("OLIMN_API_KEY", None)
if not OLIMN_API_KEY:
    raise ValueError("Please set OLIMN_API_KEY")

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

def update_host():
    # Get unique host data
    host_desc = platform_description.get_platform_description()

    # Get LAN data
    lan_desc = get_linux_wifi()

    # Get LA data
    la = get_local_area_description()

    conn = http.client.HTTPConnection("olimn.com")
    post_update(conn, "host", host_desc)
    post_update(conn, "host", lan_desc)
    post_update(conn, "host", la)

def post_update(conn, leaf, content):
    conn.request("POST", f"/vlanet/api/{leaf}", body=content, headers={"X-API-Key": OLIMN_API_KEY})
    response = conn.getresponse()
    body = response.read()
    if response.status >= 400:
        raise ConnectionError(f"POST /vlanet/api/host failed: {response.status} {response.reason}\n{body.decode()}")