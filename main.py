from fastapi import FastAPI
from contextlib import asynccontextmanager
from pymongo import ASCENDING
from common.models import APIResponse
from crawler.models import CrawlUrlsRequestBody
from database import db_manager
from config.constants import WAITING_URLS_COLLECTION, WAITING_URLS_URL_INDEX_FIELD
from celery_app import celery_fetch_url

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events
    print("Application startup: Initializing database connection...")
    try:
        await db_manager.client.admin.command("ping")
        print("Database is connected")
        await db_manager.db[WAITING_URLS_COLLECTION].create_index([(WAITING_URLS_URL_INDEX_FIELD, ASCENDING)], unique=True)
        print("All indexes are created")
    except Exception as e:
        # If ping fails, bubble up so the server won’t start
        raise RuntimeError(f"MongoDB Exception: {e}") from e
    yield
    # Shutdown events
    print("Application shutdown: Closing database connection...")
    await db_manager.client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def index():
    return {"message": "Welcome to Crawler"}

@app.post("/crawler/article-urls", response_model=APIResponse[str])
async def crawl_urls(request_body: CrawlUrlsRequestBody):
    celery_fetch_url.delay(request_body.model_dump())
    return APIResponse(data="Crawling article urls is processing")