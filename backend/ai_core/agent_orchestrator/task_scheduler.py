"""Task scheduler — priority queue for agent tasks with timeout and retry."""

import asyncio
import uuid
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import IntEnum
from loguru import logger


class Priority(IntEnum):
    CRITICAL = 0  # Kill switch, emergency stops
    HIGH = 1      # Trade execution
    NORMAL = 2    # Analysis, backtesting
    LOW = 3       # Reports, cleanup


@dataclass(order=True)
class ScheduledTask:
    priority: int
    task_id: str = field(compare=False)
    task_type: str = field(compare=False)
    params: Dict[str, Any] = field(compare=False, default_factory=dict)
    timeout: float = field(compare=False, default=30.0)
    max_retries: int = field(compare=False, default=3)
    retries: int = field(compare=False, default=0)
    status: str = field(compare=False, default="queued")
    result: Any = field(compare=False, default=None)


class TaskScheduler:
    """Priority queue based task scheduler for agent operations."""

    def __init__(self, max_concurrent: int = 5):
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._max_concurrent = max_concurrent
        self._active_count = 0
        self._tasks: Dict[str, ScheduledTask] = {}
        self._dead_letter: list = []
        self._running = False
        self._workers: list = []

    async def submit(
        self,
        task_type: str,
        params: Dict[str, Any],
        priority: Priority = Priority.NORMAL,
        timeout: float = 30.0,
    ) -> str:
        """Submit a task to the scheduler."""
        task_id = str(uuid.uuid4())[:12]
        task = ScheduledTask(
            priority=priority.value,
            task_id=task_id,
            task_type=task_type,
            params=params,
            timeout=timeout,
        )
        self._tasks[task_id] = task
        await self._queue.put(task)
        logger.debug(f"Task queued: {task_type} ({task_id}) priority={priority.name}")
        return task_id

    async def start(self, executor: Callable):
        """Start processing tasks with the given executor function."""
        self._running = True
        self._executor = executor
        for i in range(self._max_concurrent):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)
        logger.info(f"Task scheduler started with {self._max_concurrent} workers")

    async def stop(self):
        """Stop the scheduler gracefully."""
        self._running = False
        for w in self._workers:
            w.cancel()
        self._workers.clear()
        logger.info("Task scheduler stopped")

    async def _worker(self, name: str):
        while self._running:
            try:
                task = await asyncio.wait_for(self._queue.get(), timeout=5.0)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

            self._active_count += 1
            task.status = "running"
            logger.debug(f"[{name}] Processing: {task.task_type} ({task.task_id})")

            try:
                task.result = await asyncio.wait_for(
                    self._executor(task.task_type, task.params),
                    timeout=task.timeout,
                )
                task.status = "completed"
            except asyncio.TimeoutError:
                task.retries += 1
                if task.retries < task.max_retries:
                    task.status = "queued"
                    await self._queue.put(task)
                    logger.warning(f"Task timeout, retrying ({task.retries}/{task.max_retries}): {task.task_id}")
                else:
                    task.status = "dead"
                    self._dead_letter.append(task)
                    logger.error(f"Task exhausted retries: {task.task_id}")
            except Exception as e:
                task.retries += 1
                if task.retries < task.max_retries:
                    task.status = "queued"
                    await self._queue.put(task)
                else:
                    task.status = "dead"
                    task.result = {"error": str(e)}
                    self._dead_letter.append(task)
                    logger.error(f"Task failed permanently: {task.task_id} — {e}")
            finally:
                self._active_count -= 1

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        task = self._tasks.get(task_id)
        if not task:
            return None
        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "status": task.status,
            "retries": task.retries,
            "result": task.result,
        }

    def get_queue_stats(self) -> Dict:
        return {
            "queued": self._queue.qsize(),
            "active": self._active_count,
            "total_tracked": len(self._tasks),
            "dead_letter": len(self._dead_letter),
        }
