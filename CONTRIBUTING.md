# Contributing to grafana-mcp-observability

Thank you for contributing! This project is a read-only MCP server for Grafana observability.

## Reporting Issues
- Use [GitHub Issues](https://github.com/akkireddy-challa/grafana-mcp-observability/issues)
- Include: Python version, Grafana version, error message, and steps to reproduce

## Proposing New Tools

Open an issue with:
- Tool name and description
- Grafana API endpoint(s) it would use
- Example use case for on-call/platform engineering
- Read-only guarantee

## Development Setup

```bash
git clone https://github.com/akkireddy-challa/grafana-mcp-observability
cd grafana-mcp-observability
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

```bash
pytest tests/ -v --cov=server
```

## Code Style

```bash
ruff check . --fix
mypy server.py
```

## Pull Request Guidelines

1. Fork and create a branch from `main`
2. Add tests for new tools
3. Keep all tools read-only
4. Update README tool table for new tools
5. Run `ruff` and `mypy` before submitting

## License

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE).
