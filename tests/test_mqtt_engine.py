import pytest
from app.mqtt_engine import generate_payload


def test_generate_payload_fixed():
    template = {"type": "fixed", "value": 42}
    assert generate_payload(template) == 42


def test_generate_payload_range():
    template = {"type": "range", "min": 10, "max": 20}
    value = generate_payload(template)
    assert 10 <= value <= 20


def test_generate_payload_enum():
    template = {"type": "enum", "values": ["a", "b", "c"]}
    value = generate_payload(template)
    assert value in ["a", "b", "c"]


def test_generate_payload_nested():
    template = {
        "temperature": {"type": "range", "min": 0, "max": 100},
        "status": {"type": "fixed", "value": "ok"},
    }
    payload = generate_payload(template)
    assert 0 <= payload["temperature"] <= 100
    assert payload["status"] == "ok"
