"""
TaskFlow Demo Script
Developed by: visionis
Description: Showcases the asynchronous task processing and retry logic.
"""

import asyncio
import random
import sys
import os

# Ensure the parent directory is in the path so we can import 'taskflow'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from taskflow import TaskFlowEngine

async def data_handler(payload):
    """Simulates a processing task with potential for random failures."""
    await asyncio.sleep(0.5)
    
    # 25% chance to trigger an error to demonstrate the 'flow' of retries
    if random.random() < 0.25:
        raise ConnectionError("Service temporarily unavailable")
        
    print(f"TaskFlow Output: Successfully processed {payload}")

async def main():
    # Initialize the engine with visionis's preferred configuration
    flow = TaskFlowEngine(max_retries=3, workers=3)
    
    # Ignite the engine
    await flow.start(data_handler)
    
    # Feed the queue with sample data
    work_items = ["visionis_task_01", "visionis_task_02", "visionis_task_03"]
    for item in work_items:
        await flow.enqueue(item)
    
    # Gracefully finish all tasks and stop
    await flow.shutdown()

if __name__ == "__main__":
    print("--- Starting TaskFlow Demo by visionis ---")
    asyncio.run(main())
    print("--- Demo Completed ---")
