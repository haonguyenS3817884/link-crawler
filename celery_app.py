from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown
from kombu import Queue
import asyncio
from background_tasks.crawler_tasks import fetch_urls
from database import db_manager
import os

GET_URLS_QUEUE = "get_urls"

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery_app.conf.task_queues = (
    Queue(GET_URLS_QUEUE),
)

loop: asyncio.AbstractEventLoop | None = None

@worker_process_init.connect
def on_worker_process_init(**kwargs):
    global loop
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(db_manager.client.admin.command("ping"))
        print(f"[PID {os.getpid()}] Database is ready")
    except Exception as e:
        print(f"[PID {os.getpid()}] Failed to connect database: {e}")

@worker_process_shutdown.connect
def on_worker_process_shutdown(**kwargs):
    global loop
    print(f"[PID {os.getpid()}] Shutting down")
    # Close the client’s pools
    loop.run_until_complete(db_manager.client.close())
    loop.close()
    
@celery_app.task(queue=GET_URLS_QUEUE)
def celery_fetch_url(target_url: str, wait_for: int = 1000):
    loop.run_until_complete(fetch_urls(target_url=target_url, wait_for=wait_for))