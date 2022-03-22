from abc import ABC, abstractmethod


class DataRetrieverInterface(ABC):

    @abstractmethod
    def get_products(self):
        raise NotImplementedError
