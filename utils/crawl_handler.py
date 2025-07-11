from playwright.async_api import Page

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