from abc import ABC, abstractmethod


class RetrieverBuilder(ABC):

    @abstractmethod
    def build_retrievers():
        raise NotImplementedError
