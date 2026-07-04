from instantiator.instantiator import Instantiator



from host.manifest_manager import update_manifest
from host.vlanet_interface import update_host_on_vlanet

import sys

if __name__ == "__main__":
    name = sys.argv[1]

    vla_star_instantiator = Instantiator.try_load_by_name(sys.argv[1])
    if vla_star_instantiator:
        good = vla_star_instantiator.instantiate() # no args. But this should be filled.

        
    else:
        print(f"[Class 1 Instantiator] Could not find {name}")

    