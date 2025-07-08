from pydantic import BaseModel

class CrawlUrlsRequestBody(BaseModel):
    target_url: str
    wait_for: int = 1000 # milliseconds