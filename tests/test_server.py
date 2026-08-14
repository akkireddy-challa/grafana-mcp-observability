"""Unit tests for grafana-mcp-observability server.py.

These tests mock the Grafana HTTP API so they run without a live
Grafana instance. They validate:
  - Tool schema registration (list_tools)
  - Tool routing and response formatting (call_tool)
"""
import os
import sys
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("GRAFANA_TOKEN", "test-token")
os.environ.setdefault("GRAFANA_URL", "http://localhost:3000")

import server  # noqa: E402


@pytest.mark.asyncio
async def test_list_tools_returns_expected_tools():
    tools = await server.list_tools()
    names = {t.name for t in tools}
    assert names == {
        "list_dashboards",
        "get_dashboard",
        "list_datasources",
        "query_datasource",
        "list_alerts",
        "get_alert_details",
        "get_annotations",
    }


@pytest.mark.asyncio
async def test_list_dashboards_formats_output():
    fake_data = [
        {"title": "CPU Usage", "uid": "abc123", "folderTitle": "Infra"},
    ]
    with patch("server.grafana_get", new=AsyncMock(return_value=fake_data)):
        result = await server.call_tool("list_dashboards", {})
    assert "CPU Usage" in result[0].text
    assert "abc123" in result[0].text


@pytest.mark.asyncio
async def test_list_dashboards_handles_empty():
    with patch("server.grafana_get", new=AsyncMock(return_value=[])):
        result = await server.call_tool("list_dashboards", {})
    assert "No dashboards found." in result[0].text


@pytest.mark.asyncio
async def test_list_datasources_formats_output():
    fake_data = [{"name": "Prometheus", "type": "prometheus", "uid": "ds1"}]
    with patch("server.grafana_get", new=AsyncMock(return_value=fake_data)):
        result = await server.call_tool("list_datasources", {})
    assert "Prometheus" in result[0].text
    assert "ds1" in result[0].text


@pytest.mark.asyncio
async def test_get_dashboard_returns_panels():
    fake_data = {
        "dashboard": {
            "title": "My Dashboard",
            "panels": [{"title": "Panel A", "type": "graph", "id": 1}],
        }
    }
    with patch("server.grafana_get", new=AsyncMock(return_value=fake_data)):
        result = await server.call_tool("get_dashboard", {"uid": "xyz"})
    assert "My Dashboard" in result[0].text
    assert "Panel A" in result[0].text


@pytest.mark.asyncio
async def test_list_alerts_formats_output():
    fake_data = [
        {"labels": {"alertname": "HighCPU"}, "status": {"state": "active"}},
    ]
    with patch("server.grafana_get", new=AsyncMock(return_value=fake_data)):
        result = await server.call_tool("list_alerts", {})
    assert "HighCPU" in result[0].text
    assert "active" in result[0].text


@pytest.mark.asyncio
async def test_list_alerts_handles_empty():
    with patch("server.grafana_get", new=AsyncMock(return_value=[])):
        result = await server.call_tool("list_alerts", {})
    assert "No active alerts." in result[0].text


@pytest.mark.asyncio
async def test_get_annotations_formats_output():
    fake_data = [
        {"time": 1234567890, "text": "Deploy v1.2.3", "tags": ["deploy"]},
    ]
    with patch("server.grafana_get", new=AsyncMock(return_value=fake_data)):
        result = await server.call_tool("get_annotations", {})
    assert "Deploy v1.2.3" in result[0].text


@pytest.mark.asyncio
async def test_unknown_tool_returns_error_message():
    result = await server.call_tool("does_not_exist", {})
    assert "Unknown tool" in result[0].text


@pytest.mark.asyncio
async def test_get_alert_details_returns_raw_data():
    fake_data = {"uid": "alert-1", "state": "firing"}
    with patch("server.grafana_get", new=AsyncMock(return_value=fake_data)):
        result = await server.call_tool("get_alert_details", {"alert_uid": "alert-1"})
    assert "alert-1" in result[0].text
    assert "firing" in result[0].text
