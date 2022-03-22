from abc import ABC, abstractmethod


class BuilderInterface(ABC):

    @abstractmethod
    def build_retrievers():
        raise NotImplementedError
