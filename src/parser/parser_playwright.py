from typing import List
import asyncio

from playwright.async_api import async_playwright, Browser, Playwright, Page, ElementHandle

from src.parser.parser import Parser, ElementType


class PlaywrightParser(Parser):


    def __init__(
            self,
            save_path: str,
            headless: bool = True,
            proxy: list | None = None,
    ):
        self.headless = headless
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.page: Page | None = None
        self.proxy = proxy
        self.save_path = save_path

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless, proxy=self.proxy)
        context = await self.browser.new_context(viewport={"width": 1920, "height": 1080})
        self.page = await context.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print(f"{exc_type=}, {exc_val=}, {exc_tb=}")
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def load_page(
            self,
            url: str,
    ) -> None:
        self._ensure_page_init()
        await self.page.goto(url)
        await self.page.wait_for_load_state("load")

    async def get_element_by_selector(
            self,
            selector: str
    ) -> List[ElementHandle]:
        elements = await self.page.query_selector_all(selector)
        return elements

    async def get_href_from_element(
            self,
            element: ElementType
    ) -> str:
        return await element.get_attribute("href")

    async def download_html(
            self,
            filename: str
    ) -> str:
        self._ensure_page_init()

        html = await self.page.content()
        filepath = f"{self.save_path.rstrip('/')}/{filename}"
        with open(filepath, "w", encoding="UTF-8") as f:
            f.write(html)

        return filepath

    def _ensure_page_init(self) -> None:
        if not self.page:
            raise RuntimeError("Page is not init")

# async def amain():
#     try:
#         url = "https://pizza-romano.qr-cafe.ru/"
#         async with PlaywrightParser(r"C:\._programming\TeastyMenuParsing\src\parser\files",True) as parser:
#             await parser.load_page(url)
#             elements = await parser.get_element_by_selector("a")
#             path = await parser.download_html(f"page_0.txt")
#             hrefs = []
#             for i, element in enumerate(elements):
#                 href = await parser.get_href_from_element(element)
#                 if url not in href:
#                     href = url + href
#                 hrefs.append(href)
#
#             for i, href in enumerate(hrefs):
#                 try:
#                     await parser.load_page(href)
#                     path = await parser.download_html(f"page_{i+1}.txt")
#                     print(f"save page: {i=} | {href=} | {path=}")
#                 except:
#                     hrefs.append(href)
#     except Exception as e:
#         print(e)
#
# def main():
#     asyncio.run(amain())
#
# main()