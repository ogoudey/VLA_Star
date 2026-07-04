from pathlib import Path
import pickle
from vla_star.vla_star import VLA_Star
from typing import Optional
from host.host import Host
class Instantiator:
    vla_star: VLA_Star
    frozen_vla_stars: Path = Path("frozen") / "vla_stars"

    def __init__(self, vla_star: VLA_Star):
        self.vla_star = vla_star

    def instantiate(self):
        print(f"[Instantiator] Identifying Host.\r")
        host = Host()
        print(f"Asking Host to host VLA*.")
        host.host_vla_star(self.vla_star)

    @staticmethod
    def try_load_by_name(name: str) -> Optional["Instantiator"]:
        try:
            import pickle
            filepath = Instantiator.frozen_vla_stars / f"{name}.pkl"
            with open(filepath, 'rb') as f:
                vla_star = pickle.load(f)
            print(f"[Instantiator] found VLA* at {filepath}.")
            return Instantiator(vla_star)
        except ImportError:
            print("Pickle not installed. Skipping Pickle stuff")
            return None
        except FileNotFoundError:
            print(f"[Instantiator] Could not find VLA* by \"{name}\"")
            return None
        except Exception as e:
            return None

    """
    def try_pickle_configurable(self):
        try:
            import pickle
            if not self.frozen_encoded_configurables.exists():
                self.frozen_encoded_configurables.mkdir(parents=True, exist_ok=True)
            with open(self.frozen_encoded_configurables / f"{self.configurable.name_kind}.pkl", 'wb') as f:  # Overwrites any existing file.
                print(f"Writing code for {self.configurable.name_kind}...")
                pickle.dump(self.configurable, f, pickle.HIGHEST_PROTOCOL)
        except ImportError:
            print(f"Failed to pickle {self.configurable.name_kind}... skipping.")
    """
    

    def try_pickle_vla_star(self):
        try:
            if not self.frozen_vla_stars.exists():
                self.frozen_vla_stars.mkdir(parents=True, exist_ok=True)
            filepath = self.frozen_vla_stars / f"{self.vla_star.name}.pkl"
            with open(filepath, 'wb') as f:  # Overwrites any existing file.
                pickle.dump(self.vla_star, f, pickle.HIGHEST_PROTOCOL)
                print(f"[Instantiator] saved VLA* to {filepath}.")
        except ImportError:
            print(f"Failed to pickle the {self.vla_star.name}... skipping.")
        except TypeError:
            self.find_unpicklable(self.vla_star)

    def find_unpicklable(self, obj, path="root"):
        try:
            pickle.dumps(obj)
        except Exception:
            if hasattr(obj, '__dict__'):
                for k, v in obj.__dict__.items():
                    self.find_unpicklable(v, f"{path}.{k}")
            elif isinstance(obj, (list, tuple)):
                for i, v in enumerate(obj):
                    self.find_unpicklable(v, f"{path}[{i}]")
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    self.find_unpicklable(v, f"{path}[{k}]")
            else:
                print(f"UNPICKLABLE: {path} -> {type(obj)}")

