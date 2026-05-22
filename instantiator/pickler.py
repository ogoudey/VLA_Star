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
            return pickle.load(f)
    except ImportError:
        return None #silent

def try_pickle_vla_star(self, vla_star):
    try:
        import pickle
        if not self.frozen_vla_stars.exists():
            self.frozen_vla_stars.mkdir(parents=True, exist_ok=True)
        with open(self.frozen_vla_stars / f"{vla_star.name}.pkl", 'wb') as f:  # Overwrites any existing file.
            pickle.dump(self.configurable, f, pickle.HIGHEST_PROTOCOL)
    except ImportError:
        print(f"Failed to pickle the {self.configurable.name_kind} named {vla_star.name}... skipping.")
