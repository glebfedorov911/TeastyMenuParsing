from abc import abstractmethod

import httpx

from src.httpclient.http_client import HttpClient


class BaseRequestHttpxClient:

    async def send_request(self, method, url, *args, **kwargs):
        async with httpx.AsyncClient() as client:
            request = client.build_request(method, url, *args, **kwargs)
            response = await client.send(request)
            return response

class GetHttpxClient(BaseRequestHttpxClient):

    async def send_request(self, url, headers, method="GET"):
        return await super().send_request(method, url, headers=headers)

class PostHttpxClient(BaseRequestHttpxClient):

    async def send_request(self, url, headers, json, method="POST"):
        return await super().send_request(method, url, json=json, headers=headers)

class HttpxHttpClient(HttpClient):


    async def send_request(self, method, url, /, **kwargs):
        match method.lower():
            case 'get':
                return GetHttpxClient().send_request(method.upper(), url, **kwargs)
            case 'post':
                return PostHttpxClient().send_request(method.upper(), url, **kwargs)
            case _:
                raise ValueError("Not available method")