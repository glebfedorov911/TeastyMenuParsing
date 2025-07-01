import httpx

from src.httpclient.http_client import HttpClient

class BaseRequestHttpxClient:

    async def _send_request(self, method, url, *args, **kwargs):
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=30.0)) as client:
            request = client.build_request(method, url, *args, **kwargs)
            response = await client.send(request)
            return response

class GetHttpxClient(BaseRequestHttpxClient):

    async def send_request(self, url, headers):
        return await super()._send_request("GET", url, headers=headers)

class PostHttpxClient(BaseRequestHttpxClient):

    async def send_request(self, url, headers, json):
        return await super()._send_request("POST", url, json=json, headers=headers)

class HttpxHttpClient(HttpClient):


    async def send_request(self, method, url, /, **kwargs):
        client = None
        match method.lower():
            case 'get':
                client = GetHttpxClient()
            case 'post':
                client = PostHttpxClient()
            case _:
                raise ValueError("Not available method")

        return await client.send_request(url, **kwargs)