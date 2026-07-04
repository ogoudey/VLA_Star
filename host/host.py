from host import manifest_manager, vlanet_interface

class MinimalExtension:
    pass

class Host:
    def __init__(self):
        self.extension = MinimalExtension()
    
    def host_vla_star(self, vla_star):
        manifest_manager.update_manifest(vla_star.name, new_status="active", message=f"To activate {vla_star.name}, use an activator class 1. If {vla_star.name} is active, open up a textual chat terminal on PORT.")
        vlanet_interface.update_host_on_vlanet()
        print("[Host] Host starting VLA*.")
        vla_star.safe_start()
        print("[Host] Host has stopped VLA*.")
        manifest_manager.update_manifest(vla_star.name, new_status="inactive")
        vlanet_interface.update_host_on_vlanet()