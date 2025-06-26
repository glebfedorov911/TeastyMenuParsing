from abc import ABC, abstractmethod

class AI(ABC):


    @abstractmethod
    async def send_prompt(self, url: str, prompt_system: str, prompt_user: str) -> str: ...