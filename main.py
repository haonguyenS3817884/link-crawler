from fastapi import FastAPI
from crawler.services import fetch_urls
from common.models import APIResponse
from crawler.models import CrawlUrlsRequestBody

app = FastAPI()

@app.get("/")
async def index():
    return {"message": "Welcome to Crawler"}

@app.post("/crawler/article-urls", response_model=APIResponse[list[str]])
async def crawl_urls(request_body: CrawlUrlsRequestBody):
    article_urls = await fetch_urls(request_body=request_body)
    return APIResponse(data=article_urls)