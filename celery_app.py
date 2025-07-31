from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown
from kombu import Queue
import asyncio
from database import db_manager
import os
from celery_event_loop import celery_event_loop_manager

GET_URLS_QUEUE = "get_urls"

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery_app.conf.task_queues = (
    Queue(GET_URLS_QUEUE),
)

@worker_process_init.connect
def on_worker_process_init(**kwargs):
    
    celery_event_loop_manager.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(celery_event_loop_manager.loop)

    try:
        celery_event_loop_manager.loop.run_until_complete(db_manager.client.admin.command("ping"))
        print(f"[PID {os.getpid()}] Database is ready")
    except Exception as e:
        print(f"[PID {os.getpid()}] Failed to connect database: {e}")

@worker_process_shutdown.connect
def on_worker_process_shutdown(**kwargs):
    print(f"[PID {os.getpid()}] Shutting down")
    # Close the client’s pools
    celery_event_loop_manager.loop.run_until_complete(db_manager.client.close())
    celery_event_loop_manager.loop.close()
    
celery_app.conf.include = ["crawler.tasks"]