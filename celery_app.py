from celery import Celery
from kombu import Queue
import asyncio
from background_tasks.crawler_tasks import fetch_urls
from crawler.models import CrawlUrlsRequestBody

GET_URLS_QUEUE = "get_urls"

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery_app.conf.task_queues = (
    Queue(GET_URLS_QUEUE),
)

@celery_app.task(queue=GET_URLS_QUEUE)
def celery_fetch_url(request_body: dict):
    asyncio.run(fetch_urls(CrawlUrlsRequestBody(**request_body)))