from abc import abstractmethod, ABC

from typing import TypeVar, List


ElementType = TypeVar("ElementType")

class Parser(ABC):


    @abstractmethod
    def __init__(self, path_to_save, headless: bool = True, proxy: list | None = None): ...

    @abstractmethod
    async def load_page(
            self,
            url: str,
    ): ...

    @abstractmethod
    async def get_element_by_selector(
            self,
            selector: str
    ) -> List[ElementType]: ...

    @abstractmethod
    async def get_href_from_element(
            self,
            element: ElementType
    ) -> str: ...

    @abstractmethod
    async def download_html(
            self,
            filename: str
    ) -> str: ...