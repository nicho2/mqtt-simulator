from __future__ import annotations

import asyncio
import json
import random
import ssl
from dataclasses import dataclass
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt


@dataclass
class Broker:
    """MQTT broker configuration."""

    host: str
    port: int = 1883
    security: str = "tcp"  # "tcp" or "tls"
    username: Optional[str] = None
    password: Optional[str] = None
    tls_ctx: Optional[ssl.SSLContext] = None

    def configure_client(self, client: mqtt.Client) -> None:
        """Configure a client for this broker."""
        if self.username:
            client.username_pw_set(self.username, self.password)
        if self.security == "tls" and self.tls_ctx:
            client.tls_set_context(self.tls_ctx)


class SensorPublisher:
    """Publish sensor readings to a broker using the Paho async client."""

    def __init__(self, broker: Broker) -> None:
        self.broker = broker
        self.client = mqtt.Client()
        self.sensors: list[dict[str, Any]] = []
        self.tasks: list[asyncio.Task] = []
        self.running = False

    def register_sensor(self, sensor_config: Dict[str, Any]) -> None:
        """Register a sensor configuration."""
        self.sensors.append(sensor_config)

    async def _publish_sensor(self, config: Dict[str, Any]) -> None:
        topic = config.get("topic", "sensors/default")
        template = config.get("template", {})
        # target publishing rate (messages per second). Default to 100 to
        # sustain the required throughput.
        rate = config.get("rate", 100.0)
        interval = 1.0 / float(rate) if rate > 0 else 0

        while self.running:
            payload = json.dumps(generate_payload(template))
            self.client.publish(topic, payload)
            if interval:
                await asyncio.sleep(interval)
            else:
                await asyncio.sleep(0)

    async def start(self) -> None:
        """Connect to the broker and start publishing."""
        self.broker.configure_client(self.client)
        self.client.connect_async(self.broker.host, self.broker.port)
        self.client.loop_start()
        self.running = True

        for sensor in self.sensors:
            task = asyncio.create_task(self._publish_sensor(sensor))
            self.tasks.append(task)

    async def stop(self) -> None:
        """Stop publishing and disconnect."""
        self.running = False
        for task in list(self.tasks):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self.tasks.clear()
        self.client.loop_stop()
        self.client.disconnect()


def generate_payload(template: Dict[str, Any]) -> Dict[str, Any] | Any:
    """Generate a payload from a template.

    Supported node types:
    - ``fixed``: return the provided ``value``
    - ``range``: random value between ``min`` and ``max``
    - ``enum``: random choice from ``values`` list

    The function recurses into nested dictionaries.
    """

    if not isinstance(template, dict):
        return template

    node_type = template.get("type")
    if node_type == "fixed":
        return template.get("value")
    if node_type == "range":
        start = template.get("min", 0)
        end = template.get("max", 0)
        return random.uniform(start, end)
    if node_type == "enum":
        values = template.get("values", [])
        return random.choice(values) if values else None

    return {k: generate_payload(v) for k, v in template.items()}

