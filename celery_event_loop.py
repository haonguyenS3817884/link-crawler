import asyncio

class EventLoopManager:
    def __init__(self):
        self.loop: asyncio.AbstractEventLoop | None = None

celery_event_loop_manager = EventLoopManager()