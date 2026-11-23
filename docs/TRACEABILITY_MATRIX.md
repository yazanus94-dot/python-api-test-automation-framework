# Traceability matrix

Requirement → implementation → automated evidence.

| Requirement | Implementation | Automated evidence |
|---|---|---|
| Health endpoint | `app/main.py::health` | TC-CT01, TC-CT06, `smoke` |
| JWT token issue | `app/routers/auth.py`, `app/security.py` | TC-A01–A04 |
| JWT validation / expiry | `app/security.py::decode_access_token` | TC-A05–A07, TC-U02 |
| Authorization (ownership) | `app/routers/tasks.py::_owned_row` | TC-C10, TC-C11 |
| Database persistence | `app/database.py` | TC-C09 |
| CRUD operations | `app/routers/tasks.py` | TC-C01–C08, TC-CT11 |
| Pagination | `list_tasks` Query params | TC-C03, TC-N07–N08, TC-B08 |
| Input validation | `app/schemas.py` Pydantic limits | TC-N02–N05, TC-B01–B07, TC-CT04 |
| Standardized errors | `app/main.py` exception handlers | TC-CT07, TC-CT09, TC-CT10 |
| Reusable API client | `qa_framework/api_client.py` | Used by every HTTP test |
| Auth fixtures | `tests/conftest.py` | `auth_client`, `unauth_client`, `second_client` |
| Configuration | `.env.example`, `qa_framework/settings.py` | All fixtures |
| Independent test data | `helpers.unique_payload`, `task_factory` | TC-C01–C11 |
| Redacted logging | `qa_framework/logging_config.py` | TC-U03 |
| HTML/JUnit reports | pyproject `addopts` | `reports/report.html`, `reports/junit.xml` |
| Contract testing | `tests/contract/` reading `/openapi.json` | TC-CT01–CT13 |
| Markers | pyproject `[tool.pytest.ini_options]` | `pytest -m <marker>` |
| CI quality gates | `.github/workflows/ci.yml` | Ruff, format, mypy, smoke, regression |
| Docker | `Dockerfile`, `docker-compose.yml` | See README validation section |

Gaps: load testing, production secret rotation and external IdP integration are
not covered; these are declared limitations, not silent omissions.
