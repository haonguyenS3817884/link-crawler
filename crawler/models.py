from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime
from common.models import PyObjectId
from utils.convert_handler import encode_datetime
from utils.datetime_handler import utc_now

class CrawlUrlsRequestBody(BaseModel):
    target_url: str
    wait_for: int = 1000 # milliseconds

class WaitingUrl(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    url: str
    domain: str
    is_extracted: bool
    is_article_url: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        validate_by_name = True
        json_encoders = {ObjectId: str, datetime: encode_datetime}

class CreateWaitingUrl(BaseModel):
    url: str
    domain: str
    is_extracted: bool = False
    is_article_url: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)