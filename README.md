# TaskFlow 🌊

A lightweight, high-performance asynchronous task manager for Python.

## Features
- **Concurrent Workers:** Efficient task processing with `asyncio`.
- **Fault Tolerance:** Automated exponential backoff and retries.
- **Graceful Shutdown:** Ensures queue completion before exit.

## Quick Start
```python
from taskflow import TaskFlowEngine
import asyncio

async def worker(data):
    # Process your logic here
    pass

async def main():
    flow = TaskFlowEngine(workers=4)
    await flow.start(worker)
    await flow.enqueue("data")
    await flow.shutdown()

asyncio.run(main())