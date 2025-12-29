import asyncio
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Coroutine, List
from uuid import uuid4

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TaskFlow")

@dataclass
class Task:
    payload: Any
    retries: int = 0
    id: str = field(default_factory=lambda: str(uuid4())[:8])

class TaskFlowEngine:
    """High-performance async task manager with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, workers: int = 5):
        self.queue: asyncio.Queue[Task] = asyncio.Queue()
        self.max_retries = max_retries
        self.worker_count = workers
        self._workers: List[asyncio.Task] = []
        self.is_running = False

    async def enqueue(self, payload: Any):
        await self.queue.put(Task(payload=payload))

    async def _worker(self, handler: Callable[[Any], Coroutine]):
        while self.is_running:
            try:
                task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            try:
                await handler(task.payload)
                logger.info(f"Task {task.id} success.")
            except Exception as e:
                await self._handle_retry(task, e)
            finally:
                self.queue.task_done()

    async def _handle_retry(self, task: Task, error: Exception):
        if task.retries < self.max_retries:
            task.retries += 1
            delay = (2 ** task.retries) + random.uniform(0.1, 1.0)
            logger.warning(f"Task {task.id} failed. Retry {task.retries}/{self.max_retries} in {delay:.1f}s")
            await asyncio.sleep(delay)
            await self.queue.put(task)
        else:
            logger.error(f"Task {task.id} failed permanently.")

    async def start(self, handler: Callable[[Any], Coroutine]):
        self.is_running = True
        self._workers = [asyncio.create_task(self._worker(handler)) for _ in range(self.worker_count)]
        logger.info(f"Engine started | Workers: {self.worker_count}")

    async def shutdown(self):
        await self.queue.join()
        self.is_running = False
        for w in self._workers: w.cancel()
        logger.info("Engine stopped.")
