from abc import abstractmethod



class Configurable:
    pass

    @abstractmethod
    def configure(self):
        raise NotImplementedError()

