# grafana-mcp-observability

> MCP server for Grafana — query dashboards, alerts, and datasources via AI agents.

![python](https://img.shields.io/badge/python-3.11+-blue) ![Grafana](https://img.shields.io/badge/Grafana-MCP-orange) ![MCP](https://img.shields.io/badge/MCP-compatible-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What is this?

`grafana-mcp-observability` is an MCP (Model Context Protocol) server that exposes Grafana's observability stack to AI agents. It enables AI-driven incident investigation, alert triage, and dashboard querying — without requiring manual Grafana access.

Built for platform engineers who run Grafana with Prometheus, Loki, or Tempo as their observability backend.

---

## Available Tools

| Tool | Description |
|---|---|
| `list_dashboards` | List all Grafana dashboards by folder |
| `get_dashboard` | Fetch a dashboard's panel definitions and queries |
| `query_datasource` | Run a PromQL or LogQL query against a datasource |
| `list_alerts` | List active and pending alert rules |
| `get_alert_details` | Get labels, annotations, and state for a specific alert |
| `list_datasources` | List configured datasources (Prometheus, Loki, Tempo, etc.) |
| `get_annotations` | Fetch deployment or event annotations from dashboards |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Grafana instance with API access
- Grafana Service Account token with `Viewer` role

### Installation

```bash
git clone https://github.com/akkireddy-challa/grafana-mcp-observability
cd grafana-mcp-observability
pip install -r requirements.txt
```

### Configuration

```bash
export GRAFANA_URL=https://grafana.example.com
export GRAFANA_TOKEN=<service-account-token>
```

### Run

```bash
python server.py
```

### MCP Client Config (Claude Desktop)

```json
{
  "mcpServers": {
    "grafana": {
      "command": "python",
      "args": ["/path/to/grafana-mcp-observability/server.py"],
      "env": {
        "GRAFANA_URL": "https://grafana.example.com",
        "GRAFANA_TOKEN": "<your-token>"
      }
    }
  }
}
```

---

## Security Model

- Uses Grafana **Service Account tokens** — not user credentials
- Token requires `Viewer` role only — no write access needed
- No dashboard modifications or alert rule changes are possible
- All queries are read-only
- Token stored in environment variables, never in code

---

## Use Cases at Telia

This pattern is used to allow AI agents to:

- Investigate active alerts by querying Prometheus metrics in context
- Correlate Loki log spikes with Grafana annotation events (deployments)
- Summarize dashboard panel state for on-call briefings
- Detect anomalous query patterns across multi-tenant Grafana orgs

---

## Roadmap

- [ ] `get_traces` — query Tempo distributed traces
- [ ] `create_annotation` — mark AI-driven investigation events
- [ ] `silence_alert` — create Alertmanager silences via MCP
- [ ] Multi-org Grafana support
- [ ] GitHub Actions workflow for CI validation

---

## Related Projects

| Repo | Purpose |
|---|---|
| [k8s-mcp-server](https://github.com/akkireddy-challa/k8s-mcp-server) | Kubernetes cluster diagnostics via MCP |
| [azure-mcp-platform](https://github.com/akkireddy-challa/azure-mcp-platform) | Azure resource management via MCP |
| [phoenix-mcp-eval](https://github.com/akkireddy-challa/phoenix-mcp-eval) | LLM tracing and evaluation via MCP |

---

## License

MIT License. See [LICENSE](LICENSE) for details.
