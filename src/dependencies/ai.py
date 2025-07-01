import os

from fastapi import Depends

from src.ai.chatgpt_ai import ChatGptAI
from src.dependencies.http_client import get_httpx_http_client
from src.httpclient.httpx_http_client import HttpxHttpClient


def get_chatgpt_ai(
        http_client: HttpxHttpClient = Depends(get_httpx_http_client),
) -> ChatGptAI:
    return ChatGptAI(http_client=http_client, auth_token=os.getenv("TOKEN_GPT"))