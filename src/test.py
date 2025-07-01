from urllib.parse import urljoin
import asyncio

from src.ai.chatgpt_ai import ChatGptAI
from src.httpclient.httpx_http_client import HttpxHttpClient


client = HttpxHttpClient()

ai = ChatGptAI(token, client)

async def send_prompt():
    url = "https://api.openai.com/v1/chat/completions"
    prompt_system = "Ты парсишь данные"

    with open(r"C:\._programming\TeastyMenuParsing\src\ai\file.txt", "r", encoding="utf-8") as f:
        file_content = f.read()

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(file_content, "html.parser")
    for tag in soup(["style", "script"]):
        tag.decompose()

    file_content = str(soup)

    prompt_user = f"""
        Твоя задача спарсить данные, если они есть такие как
        ингредиенты, название, описание, цену, картинку, категорию (если нет, то придумай сам по типу товара)
        верни это json'ом ingredients: [], name: "", desc: "", price: "", img: "", category: "",
        если ничего найти не можешь или тебе кажется что это бред, то просто верни пустой json (две фигурные скобки),
        я тебе буду кидать страницу по кусочкам, вот парси отсюда
        {file_content}"""

    result = await ai.send_prompt(url, prompt_system, prompt_user)
    contents = result["choices"][0]["message"]["content"]
    try:
        import json
        contents = json.loads(contents)
        if contents != {}:
            for content in contents:
                img = urljoin("https://pizza-romano.qr-cafe.ru/", content.get('img'))
                print(f"name = {content.get('name')}")
                print(f"desc = {content.get('desc')}")
                print(f"ingredients = {content.get('ingredients')}")
                print(f"price = {content.get('price')}")
                print(f"img = {img}")
                print(f"category = {content.get('category')}")
    except:
        ...

def main():
    asyncio.run(send_prompt())

if __name__ == "__main__":
    main()