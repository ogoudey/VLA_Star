from instantiator.instantiators.chatter_instantiator import ChatterInstantiator

from host.manifest_manager import update_manifest
from host.vlanet_interface import update_host_on_vlanet

import sys

if __name__ == "__main__":
    spec = ChatterInstantiator("norm")

    ### Individualization
    vla_star = spec.instantiate(
        name=sys.argv[1],
        recorded=True,
        extra="\nAbove all, refer to yourself INCESSANTLY as a guinea pig. Bring it up ALL THE TIME.",
        chat_port=int(sys.argv[2])
    )

    update_manifest(sys.argv[1], new_status="active", message="To activate Fred, use an activator level 1. If fred is active, open up a chat port with a textual chat port.")

    update_host_on_vlanet()

    vla_star.safe_start()

    update_manifest(sys.argv[1], new_status="inactive")

    update_host_on_vlanet()