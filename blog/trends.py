import asyncio
import json
import random
from pathlib import Path

from aiohttp import ClientSession
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


class GoogleTrendsScraper:
    def __init__(self, keyword: str, headless: bool = True):
        self.keyword = keyword
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.related_searches_api_url = None

    async def _init_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
            ]
        )

        self.context = await self.browser.new_context(
            user_agent=random.choice(self._user_agents()),
            viewport={"width": 1280, "height": 800},
            locale='en-US'
        )
        self.page = await self.context.new_page()

    async def _capture_api_call(self):
        async def route_handler(route, request):
            if 'widgetdata/relatedsearches' in request.url:
                self.related_searches_api_url = request.url
                # print(f"[Captured] {self.related_searches_api_url}")
            await route.continue_()

        await self.page.route("**/*", route_handler)

    async def _visit_embed_page(self):
        embed_url = self._generate_embed_url()
        print(f"Navigating to: {embed_url}")
        await self.page.goto(embed_url, timeout=60000)
        await self.page.wait_for_selector("body", timeout=10000)
        await self.page.reload()  # Ensure network calls are made
        await asyncio.sleep(5)  # Give time for the API to fire

    async def _download_related_searches_json(self):
        if not self.related_searches_api_url:
            print("Related searches API URL not found.")
            return

        async with ClientSession() as session:
            async with session.get(self.related_searches_api_url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                if resp.status != 200:
                    print(f"Failed to fetch JSON. Status: {resp.status}")
                    return

                raw_data = await resp.text()
                clean_data = raw_data.split("\n", 1)[1] if raw_data.startswith(")]}',") else raw_data
                self._save_json(clean_data)
                print(f"Saved: related_searches.json")

    def _save_json(self, data: str):
        Path(f"related_searches.json").write_text(data)

    def _generate_embed_url(self) -> str:
        payload = {
            "comparisonItem": [{"keyword": self.keyword, "geo": "IN", "time": "today 12-m"}],
            "category": 0,
            "property": ""
        }
        return (
            "https://trends.google.com/trends/embed/explore/RELATED_QUERIES"
            f"?hl=en&tz=420&req={json.dumps(payload)}"
        )

    def _user_agents(self):
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
        ]

    async def run(self):
        await self._init_browser()
        try:
            await self._capture_api_call()
            await self._visit_embed_page()
            await self._download_related_searches_json()
        except PlaywrightTimeoutError:
            print("Timeout while loading the page or API.")
        finally:
            await self._cleanup()

    async def _cleanup(self):
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()
        print("Browser closed.")


async def main():
    keyword = "hacking"
    scraper = GoogleTrendsScraper(keyword, headless=False)
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
