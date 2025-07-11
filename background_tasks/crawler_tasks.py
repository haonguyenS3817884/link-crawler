from playwright.async_api import async_playwright
from urllib.parse import urljoin
import asyncio
from crawler.models import CrawlUrlsRequestBody, CreateWaitingUrl
from utils.url_handler import get_domain, get_domain_url
from crawler.repository import insert_url
from utils.crawl_handler import get_all_hrefs, scroll_all_page

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