from playwright.async_api import async_playwright
from urllib.parse import urljoin
import asyncio
from celery_app import celery_app, GET_URLS_QUEUE
from celery_event_loop import celery_event_loop_manager
from utils.url_handler import get_domain, get_domain_url
from utils.crawl_handler import get_all_hrefs, scroll_all_page
from .repository import insert_url
from .models import CreateWaitingUrl

async def fetch_urls(target_url: str, wait_for: int = 1000):
    urls = set()
    insert_operations = []
    domain = get_domain(url=target_url)
    domain_url = get_domain_url(url=target_url)
    
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(target_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(wait_for)
        
        await scroll_all_page(page=page, wait_for=wait_for)
        
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

@celery_app.task(queue=GET_URLS_QUEUE)
def celery_fetch_url(target_url: str, wait_for: int = 1000):
    celery_event_loop_manager.loop.run_until_complete(fetch_urls(target_url=target_url, wait_for=wait_for))