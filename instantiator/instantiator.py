from pathlib import Path

from vla_star_configurable.vla_star_configurable import VLA_Star_Configurable
from vla_star_configurable.vla_star_config.vla_star_types import *
from vla_star.vla_star import VLA_Star

class Instantiator:
    configurable: VLA_Star_Configurable
    frozen_encoded_configurables: Path = Path("frozen") / "configurables"
    frozen_vla_stars: Path = Path("frozen") / "vla_stars"

    def instantiate(self, **kwargs) -> VLA_Star:
        print("Instantiating...")
        vla_star = self.configurable.instantiate(**kwargs)
        try:
            self.try_pickle_vla_star(vla_star)
        except Exception as e:
            print(f"Failed: {e}")
        return vla_star


    def try_pickle_configurable(self):
        try:
            import pickle
            if not self.frozen_encoded_configurables.exists():
                self.frozen_encoded_configurables.mkdir(parents=True, exist_ok=True)
            with open(self.frozen_encoded_configurables / f"{self.configurable.name_kind}.pkl", 'wb') as f:  # Overwrites any existing file.
                pickle.dump(self.configurable, f, pickle.HIGHEST_PROTOCOL)
        except ImportError:
            print(f"Failed to pickle {self.configurable.name_kind}... skipping.")

    def try_load_configurable(self, name_kind):
        try:
            import pickle
            with open(self.frozen_encoded_configurables / f"{name_kind}.pkl", 'rb') as f:
                self.configurable = pickle.load(f)
            print(f"Using existing code for {name_kind}.")
            return True
        except ImportError:
            return False #silent

    def try_pickle_vla_star(self, vla_star):
        try:
            import pickle
            if not self.frozen_vla_stars.exists():
                self.frozen_vla_stars.mkdir(parents=True, exist_ok=True)
            with open(self.frozen_vla_stars / f"{vla_star.name}.pkl", 'wb') as f:  # Overwrites any existing file.
                pickle.dump(self.configurable, f, pickle.HIGHEST_PROTOCOL)
        except ImportError:
            print(f"Failed to pickle the {self.configurable.name_kind} named {vla_star.name}... skipping.")


