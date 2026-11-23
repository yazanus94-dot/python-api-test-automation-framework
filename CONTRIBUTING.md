# Contributing

1. Fork or create a feature branch from `main`.
2. Install dependencies: `pip install -r requirements.txt -r requirements-dev.txt`.
3. Copy `.env.example` to `.env` for local configuration; never commit `.env`.
4. Add or update tests for every behavior change; keep scenarios independent and
   use `task_factory` for cleanup.
5. Run local gates: `ruff check .`, `ruff format --check .`,
   `mypy app qa_framework`, `python -m pytest`.
6. Open a pull request; CI must pass on Python 3.12.

## Test authoring rules

- Use real HTTP through `ApiClient`; do not mock `requests`.
- Redact credentials in any new logging.
- Use explicit markers from `pyproject.toml`.
- Add a `TC-...` row to `docs/TEST_CASES.md` and the traceability matrix.

## Security

Never commit tokens, `.env`, database files or reports. `JWT_SECRET_KEY` must be
supplied by the environment in any shared deployment.
