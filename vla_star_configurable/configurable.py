import inspect
from abc import abstractmethod

class Configurable:
    def instantiate_with_filtered_args(self, func, kwargs):
        valid = inspect.signature(func).parameters
        kwargs = {k: v for k, v in kwargs.items() if k in valid}
        return func(**kwargs)
    
    def build_with_filtered_args(self, func, kwargs):
        valid = inspect.signature(func).parameters
        kwargs = {k: v for k, v in kwargs.items() if k in valid}
        return func(**kwargs)
    
    @abstractmethod
    def instantiate(self):
        raise NotImplementedError()