from abc import ABC, abstractmethod


class QRReader(ABC):

    @abstractmethod
    def read(self, path: str) -> str: ...