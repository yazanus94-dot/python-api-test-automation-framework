# Test plan

## Scope

Black-box HTTP testing of the Task Management API plus lightweight unit checks
of framework utilities. All API tests issue genuine requests over localhost;
there are no mocked HTTP responses.

## Test levels and markers

| Marker | Purpose | Typical count |
|---|---|---|
| `smoke` | Critical path: health, login, list, create | 4 |
| `regression` | Full functional coverage, excluding smoke (`regression and not smoke`) | 48 |
| `authentication` | Login failures, token failures, authorization | 8 |
| `negative` | Malformed/unauthorized/unsupported requests | 16 |
| `contract` | OpenAPI, schemas, status codes, content types | 13 |
| `integration` | Multi-step CRUD and persistence flows | 11 |
| `unit` | Framework helpers without HTTP | 4 |

Markers overlap by design; the total unique scenario count is 52.

## Environment

- Python 3.12, pytest, requests, pytest-html, jsonschema.
- Isolated SQLite database per test session; seeded users from configuration.
- Uvicorn host `127.0.0.1`, port 8765 (override with `TEST_PORT`).

## Entry criteria

- Dependencies installed from `requirements.txt` and `requirements-dev.txt`.
- `/health` returns 200 within 20 seconds.
- No pre-existing test data required.

## Exit criteria

- 52 tests pass; zero failures.
- Ruff check and format check clean; mypy clean.
- HTML and JUnit reports generated in `reports/`.

## Risk coverage

- Authentication errors leak no credentials in responses or logs.
- Ownership checks prevent cross-user reads/writes (403).
- Input validation uses Pydantic limits and returns a consistent error envelope.
- Contract tests read the live OpenAPI document rather than a hand-copied spec.

## Out of scope

- Load/performance testing, browser UI, third-party identity providers,
  production secret management and real-world datasets.
