from starter.starter import Starter



from host.manifest_manager import update_manifest
from host.vlanet_interface import update_host_on_vlanet

import sys

if __name__ == "__main__":
    name = sys.argv[1]

    vla_star_starter = Starter.try_load_by_name(sys.argv[1])
    if vla_star_starter:
        good = vla_star_starter.start() # no args. But this should be filled.
    else:
        print(f"[Class 1 Start Script] Could not find {name}")

    