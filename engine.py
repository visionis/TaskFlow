import asyncio
import logging
import random
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, List
from uuid import uuid4

# Configure logging for professional output
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TaskFlow")

@dataclass
class Task:
    """Represents a unit of work with unique identification and retry tracking."""
    payload: Any
    retries: int = 0
    id: str = field(default_factory=lambda: str(uuid4())[:8])

class TaskFlowEngine:
    """
    Asynchronous task execution engine featuring a worker pool,
    concurrency control, and exponential backoff retry logic.
    """
    
    def __init__(self, max_retries: int = 3, workers: int = 5):
        self.queue: asyncio.Queue[Task] = asyncio.Queue()
        self.max_retries = max_retries
        self.worker_count = workers
        self._workers: List[asyncio.Task] = []
        self.is_running = False

    async def enqueue(self, payload: Any):
        """Wraps payload into a Task and adds it to the internal queue."""
        task = Task(payload=payload)
        await self.queue.put(task)
        logger.debug(f"Task {task.id} enqueued.")

    async def _worker(self, handler: Callable[[Any], Coroutine]):
        """Internal worker loop for consuming and processing tasks."""
        while self.is_running:
            try:
                # Polling mechanism to allow for graceful shutdown signals
                task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            try:
                await handler(task.payload)
                logger.info(f"Task {task.id} processed successfully.")
            except Exception as e:
                await self._handle_retry(task, e)
            finally:
                self.queue.task_done()

    async def _handle_retry(self, task: Task, error: Exception):
        """Implements retry logic with exponential backoff and jitter."""
        if task.retries < self.max_retries:
            task.retries += 1
            # Calculate backoff: 2^retries + random jitter
            delay = (2 ** task.retries) + random.uniform(0.1, 1.0)
            logger.warning(f"Task {task.id} attempt {task.retries} failed: {error}. Retrying in {delay:.1f}s.")
            await asyncio.sleep(delay)
            await self.queue.put(task)
        else:
            logger.error(f"Task {task.id} failed after {self.max_retries} retries. Task dropped.")

    async def start(self, handler: Callable[[Any], Coroutine]):
        """Bootstraps the worker pool and begins task processing."""
        self.is_running = True
        self._workers = [
            asyncio.create_task(self._worker(handler)) 
            for _ in range(self.worker_count)
        ]
        logger.info(f"TaskFlow engine initialized with {self.worker_count} workers.")

    async def shutdown(self):
        """Gracefully drains the queue and terminates all active workers."""
        logger.info("Initiating graceful shutdown. Draining task queue...")
        await self.queue.join()
        self.is_running = False
        for worker in self._workers:
            worker.cancel()
        logger.info("TaskFlow engine stopped.")
