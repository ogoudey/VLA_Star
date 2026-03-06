#!/usr/bin/env python3
import sys
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener

SERVICE_TYPE = "_bed._tcp.local."

result = {}

class VLAListener(ServiceListener):
    def add_service(self, zeroconf, type_, name):
        info = zeroconf.get_service_info(type_, name)
        if info:
            props = {k.decode(): v.decode() for k, v in info.properties.items()}
            username = props.get("username")
            hostname = info.server.rstrip(".")
            if username and hostname:
                result["username"] = username
                result["hostname"] = hostname

zeroconf = Zeroconf()
listener = VLAListener()
browser = ServiceBrowser(zeroconf, SERVICE_TYPE, listener)

# Wait until result is filled (with a timeout)
import time
timeout = 10  # seconds
start = time.time()
while "username" not in result and time.time() - start < timeout:
    time.sleep(0.1)

zeroconf.close()

if "username" in result:
    print(f'{result["username"]} {result["hostname"]}')
    sys.exit(0)
else:
    sys.exit(1)
