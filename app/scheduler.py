from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Any, Optional, List

import aiosqlite


class Scheduler:
    """Schedule periodic MQTT publications and record them."""

    def __init__(self, db_path: str = "publications.db") -> None:
        self.db_path = db_path
        self.db: Optional[aiosqlite.Connection] = None
        self.tasks: List[asyncio.Task] = []
        self.purge_task: Optional[asyncio.Task] = None
        self.running = False

    async def start(self) -> None:
        """Initialize database and start purge loop."""
        self.running = True
        self.db = await aiosqlite.connect(self.db_path)
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS publications(
                ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sensor_id TEXT,
                topic TEXT,
                qos INTEGER,
                payload TEXT
            )
            """
        )
        await self.db.commit()
        self.purge_task = asyncio.create_task(self._purge_loop())

    async def stop(self) -> None:
        """Cancel scheduled tasks and close the database."""
        self.running = False
        for task in list(self.tasks):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self.tasks.clear()
        if self.purge_task:
            self.purge_task.cancel()
            try:
                await self.purge_task
            except asyncio.CancelledError:
                pass
            self.purge_task = None
        if self.db:
            await self.db.close()
            self.db = None

    def schedule_publish(
        self,
        period_ms: int,
        sensor_id: str,
        topic: str,
        qos: int,
        publish_cb: Callable[[str, Any, int], Awaitable[Any]],
        payload_supplier: Callable[[], Any],
    ) -> asyncio.Task:
        """Schedule periodic publishing of a payload."""
        if not self.running:
            raise RuntimeError("Scheduler has not been started")
        task = asyncio.create_task(
            self._publish_loop(period_ms, sensor_id, topic, qos, publish_cb, payload_supplier)
        )
        self.tasks.append(task)
        return task

    async def _publish_loop(
        self,
        period_ms: int,
        sensor_id: str,
        topic: str,
        qos: int,
        publish_cb: Callable[[str, Any, int], Awaitable[Any]],
        payload_supplier: Callable[[], Any],
    ) -> None:
        interval = period_ms / 1000.0
        while self.running:
            payload = payload_supplier()
            await publish_cb(topic, payload, qos)
            await self.record_publication(sensor_id, topic, qos, payload)
            await asyncio.sleep(interval)

    async def record_publication(
        self, sensor_id: str, topic: str, qos: int, payload: Any
    ) -> None:
        """Insert a publication record into the database."""
        if not self.db:
            return
        await self.db.execute(
            "INSERT INTO publications(sensor_id, topic, qos, payload) VALUES (?,?,?,?)",
            (sensor_id, topic, qos, str(payload)),
        )
        await self.db.commit()

    async def _purge_loop(self) -> None:
        while self.running:
            await self.purge_old()
            await asyncio.sleep(24 * 60 * 60)

    async def purge_old(self) -> None:
        """Delete publication rows older than 30 days."""
        if not self.db:
            return
        await self.db.execute(
            "DELETE FROM publications WHERE ts < date('now','-30 day')"
        )
        await self.db.commit()
