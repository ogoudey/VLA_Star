from ..instantiator import MobileManipulatorInstantiator

if __name__ == "__main__":
    spec = MobileManipulatorInstantiator("unity")

    ### Individualization
    spec.instantiate(
        name="Fred",
        recorded=True,
        extra="\nAbove all, refer to yourself INCESSANTLY as a guinea pig. Bring it up ALL THE TIME."
    )