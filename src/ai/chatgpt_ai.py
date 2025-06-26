import httpx

from src.ai.ai import AI
from src.httpclient.http_client import HttpClient


class ChatGptAI(AI):


    def __init__(
            self,
            auth_token: str,
            http_client: HttpClient,
            model: str = "o4-mini",
    ):
        self.auth_token = auth_token
        self.model = model
        self.http_client = http_client

    async def send_prompt(self, url: str, prompt_system: str, prompt_user: str) -> dict:
        headers = self._create_headers()
        json = self._create_prompt(prompt_system, prompt_user)
        response = await self.http_client.send_request("POST", url, headers=headers, json=json)
        return response.json()

    def _create_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.auth_token}",
        }

    def _create_prompt(self, prompt_system: str, prompt_user: str) -> dict:
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user},
            ]
        }