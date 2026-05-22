from instantiator.instantiators.mobile_manipulator_instantiator import MobileManipulatorInstantiator

from host.manifest_manager import update_manifest
from host.vlanet_interface import update_host

if __name__ == "__main__":
    spec = MobileManipulatorInstantiator("unity")

    ### Individualization
    vla_star = spec.instantiate(
        name="Fred",
        recorded=True,
        extra="\nAbove all, refer to yourself INCESSANTLY as a guinea pig. Bring it up ALL THE TIME."
    )

    update_manifest("Fred", new_status="active", message="To activate Fred, use an activator level 1")

    update_host()

    vla_star.safe_start()

    update_manifest("Fred", new_status="inactive")


    
