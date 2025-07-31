from fastapi import APIRouter
from common.models import APIResponse
from .tasks import celery_fetch_url
from .models import CrawlUrlsRequestBody

router = APIRouter(
    prefix="/crawler"
)

@router.post("/article-urls", response_model=APIResponse[str])
async def crawl_urls(request_body: CrawlUrlsRequestBody):
    for target_url in request_body.target_urls:
        celery_fetch_url.delay(target_url, request_body.wait_for)
    return APIResponse(data="Crawling article urls is processing")