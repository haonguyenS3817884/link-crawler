from playwright.async_api import async_playwright, Page
from urllib.parse import urljoin
import asyncio
from .models import CrawlUrlsRequestBody, CreateWaitingUrl
from utils.url_handler import get_domain, get_domain_url
from .repository import insert_url

async def get_all_hrefs(page: Page):
    hrefs = await page.eval_on_selector_all(
        "a[href]",
        """(elements) => elements.map(el => el.href.trim()).filter(href => href.length > 0)"""
    )
    return hrefs

async def scroll_all_page(page: Page, wait_for: int = 1000):
    prev_height = await page.evaluate("() => document.documentElement.scrollHeight")
    print(f"Inital height: {prev_height}")
    while True:
        await page.evaluate("() => window.scrollBy(0, document.documentElement.scrollHeight)")
        await page.wait_for_timeout(wait_for)
        curr_height = await page.evaluate("() => document.documentElement.scrollHeight")
        if curr_height == prev_height:
            print("Stopped (no more content).")
            break
        prev_height = curr_height
        print(f"Current Height: {curr_height}")


async def fetch_urls(request_body: CrawlUrlsRequestBody):
    urls = set()
    insert_operations = []
    domain = get_domain(url=request_body.target_url)
    domain_url = get_domain_url(url=request_body.target_url)
    
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(request_body.target_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(request_body.wait_for)
        
        await scroll_all_page(page=page, wait_for=request_body.wait_for)
        
        hrefs = await get_all_hrefs(page=page)
        for href in hrefs:
            joined_href = urljoin(domain_url, href)
            href_domain = get_domain(joined_href)
            if href_domain == domain:
                if joined_href not in urls:
                    urls.add(joined_href)
                    insert_operations.append(insert_url(CreateWaitingUrl(url=joined_href, domain=domain_url)))
        
        print(f"{len(urls)} article urls are found")
        await asyncio.gather(*insert_operations)
        await browser.close()