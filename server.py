"""grafana-mcp-observability: MCP server for Grafana observability stack.

Exposes Grafana dashboards, alerts, datasources, and annotations
via the Model Context Protocol (MCP).

Author: Akkireddy Challa
License: MIT
"""

import os
import asyncio
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GRAFANA_URL = os.environ.get("GRAFANA_URL", "http://localhost:3000").rstrip("/")
GRAFANA_TOKEN = os.environ.get("GRAFANA_TOKEN", "")

HEADERS = {
    "Authorization": f"Bearer {GRAFANA_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
async def grafana_get(path: str, params: dict | None = None) -> Any:
    """Make a GET request to Grafana HTTP API."""
    async with httpx.AsyncClient(headers=HEADERS, timeout=30.0) as client:
        resp = await client.get(f"{GRAFANA_URL}{path}", params=params)
        resp.raise_for_status()
        return resp.json()

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
server = Server("grafana-mcp-observability")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_dashboards",
            description="List all Grafana dashboards, optionally filtered by folder.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_id": {"type": "integer", "description": "Folder ID to filter (optional)"},
                },
                "required": [],
            },
        ),
        Tool(
            name="get_dashboard",
            description="Fetch a dashboard by UID — returns panel definitions and queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "uid": {"type": "string", "description": "Dashboard UID"},
                },
                "required": ["uid"],
            },
        ),
        Tool(
            name="list_datasources",
            description="List all configured datasources (Prometheus, Loki, Tempo, etc.).",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="query_datasource",
            description="Run a PromQL or LogQL query against a named datasource.",
            inputSchema={
                "type": "object",
                "properties": {
                    "datasource_uid": {"type": "string", "description": "Datasource UID"},
                    "query": {"type": "string", "description": "PromQL or LogQL expression"},
                    "start": {"type": "string", "description": "Start time (ISO8601 or relative like 'now-1h')"},
                    "end": {"type": "string", "description": "End time (ISO8601 or 'now')"},
                },
                "required": ["datasource_uid", "query"],
            },
        ),
        Tool(
            name="list_alerts",
            description="List active and pending Grafana alert rules.",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {"type": "string", "description": "Filter by state: firing, pending, normal"},
                },
                "required": [],
            },
        ),
        Tool(
            name="get_alert_details",
            description="Get labels, annotations, and current state for a specific alert rule.",
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_uid": {"type": "string", "description": "Alert rule UID"},
                },
                "required": ["alert_uid"],
            },
        ),
        Tool(
            name="get_annotations",
            description="Fetch dashboard annotations (deployment events, incidents, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard_id": {"type": "integer", "description": "Dashboard ID (optional)"},
                    "limit": {"type": "integer", "description": "Max annotations to return (default 100)"},
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Route MCP tool calls to Grafana HTTP API."""

    if name == "list_dashboards":
        params = {}
        if folder_id := arguments.get("folder_id"):
            params["folderIds"] = folder_id
        data = await grafana_get("/api/search", params={"type": "dash-db", **params})
        lines = [f"{d['title']} (uid={d['uid']}, folder={d.get('folderTitle', 'General')})" for d in data]
        return [TextContent(type="text", text="\n".join(lines) or "No dashboards found.")]

    elif name == "get_dashboard":
        data = await grafana_get(f"/api/dashboards/uid/{arguments['uid']}")
        dashboard = data.get("dashboard", {})
        panels = [{"title": p.get("title"), "type": p.get("type"), "id": p.get("id")} for p in dashboard.get("panels", [])]
        return [TextContent(type="text", text=f"Dashboard: {dashboard.get('title')}\nPanels: {panels}")]

    elif name == "list_datasources":
        data = await grafana_get("/api/datasources")
        lines = [f"{ds['name']} (type={ds['type']}, uid={ds['uid']})" for ds in data]
        return [TextContent(type="text", text="\n".join(lines) or "No datasources found.")]

    elif name == "query_datasource":
        uid = arguments["datasource_uid"]
        query = arguments["query"]
        start = arguments.get("start", "now-1h")
        end = arguments.get("end", "now")
        payload = {
            "queries": [{"refId": "A", "expr": query, "datasource": {"uid": uid}}],
            "from": start,
            "to": end,
        }
        async with httpx.AsyncClient(headers=HEADERS, timeout=30.0) as client:
            resp = await client.post(f"{GRAFANA_URL}/api/ds/query", json=payload)
            resp.raise_for_status()
            return [TextContent(type="text", text=str(resp.json()))]

    elif name == "list_alerts":
        state = arguments.get("state")
        params = {"state": state} if state else {}
        data = await grafana_get("/api/alertmanager/grafana/api/v2/alerts", params=params)
        lines = [f"{a.get('labels', {}).get('alertname', 'unknown')} - {a.get('status', {}).get('state', 'unknown')}" for a in data]
        return [TextContent(type="text", text="\n".join(lines) or "No active alerts.")]

    elif name == "get_alert_details":
        data = await grafana_get(f"/api/ruler/grafana/api/v1/rule/{arguments['alert_uid']}")
        return [TextContent(type="text", text=str(data))]

    elif name == "get_annotations":
        params: dict = {"limit": arguments.get("limit", 100)}
        if dashboard_id := arguments.get("dashboard_id"):
            params["dashboardId"] = dashboard_id
        data = await grafana_get("/api/annotations", params=params)
        lines = [f"[{a.get('time')}] {a.get('text', '')} (tags={a.get('tags', [])})" for a in data]
        return [TextContent(type="text", text="\n".join(lines) or "No annotations found.")]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
async def main():
    if not GRAFANA_TOKEN:
        raise ValueError("GRAFANA_TOKEN environment variable is required.")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="grafana-mcp-observability",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
