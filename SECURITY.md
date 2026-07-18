# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x | Yes |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Email: **challaakkireddy@gmail.com**

Include: description, steps to reproduce, potential impact, and suggested mitigations. We respond within **48 hours**.

## Security Design Principles

1. **Read-only by default** — All tools query Grafana; no dashboard creation, deletion, or modification.
2. **Service Account tokens only** — Uses Grafana Service Account tokens with `Viewer` role. No admin tokens needed.
3. **Token isolation** — `GRAFANA_TOKEN` stored in environment variables, never in code or logs.
4. **No data-plane access** — Tools return metadata, panel structure, and query results; not raw time-series data volumes.
5. **No credential forwarding** — Datasource credentials remain in Grafana; this server only proxies queries via Grafana's API.

## Threat Model

| Threat | Mitigation |
|---|---|
| Token leakage in logs | Token never logged; only used in Authorization header |
| Over-privileged token | Viewer role enforced; no Editor/Admin scope needed |
| Injection via queries | Query strings are passed as-is to Grafana API; no shell execution |
| Unauthorized Grafana access | Server requires valid token; no anonymous fallback |
| Supply chain attack | Pin dependencies; run `pip audit` in CI |

## Responsible Disclosure

Security fixes released as patch versions with a corresponding advisory.
