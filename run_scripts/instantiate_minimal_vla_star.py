from instantiator.instantiators.chatter_instantiator import ChatterInstantiator

from host.manifest_manager import update_manifest
from host.vlanet_interface import update_host

import sys

if __name__ == "__main__":
    spec = ChatterInstantiator("norm")

    ### Individualization
    vla_star = spec.instantiate(
        name=sys.argv[1],
        recorded=True,
        extra="\nAbove all, refer to yourself INCESSANTLY as a guinea pig. Bring it up ALL THE TIME."
    )

    update_manifest("Fred", new_status="active", message="To activate Fred, use an activator level 1")

    update_host()

    vla_star.safe_start()

    update_manifest("Fred", new_status="inactive")


    
