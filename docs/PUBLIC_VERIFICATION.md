# Public verification evidence

This document records how the published state of this repository was verified
with the GitHub CLI and raw public file URLs. It exists so that the review
items can be checked without relying on a verbal summary.

## Repository identity and history

Commands used:

```bash
gh api user --jq .login
git ls-remote origin refs/heads/main
gh api repos/yazanus94-dot/python-api-test-automation-framework/commits/main --jq .sha
gh api repos/yazanus94-dot/python-api-test-automation-framework/commits --jq length
git status --short --branch
git log -5 --oneline
```

Verified result at the time of writing:

- Authenticated account: `yazanus94-dot`
- Remote HEAD: `039d081ef3247eb04774fd28ac676c256bc6e627`
- Commit count: 4
- Default branch: `main`, visibility: `public`
- Local branch: `main...origin/main`, working tree clean

## Review items checked against public raw files

Raw base URL:
`https://raw.githubusercontent.com/yazanus94-dot/python-api-test-automation-framework/main`

| Review item | Public file checked | Verified evidence |
|---|---|---|
| HTTP persistence test | `tests/api/test_tasks_crud.py` | no `sqlite3`, no `db_connection`; `ApiClient(base_url, token=auth_token)` performs POST/GET and asserts id, title, description, status, owner |
| Mutually exclusive markers | `tests/api/test_auth.py`, `tests/api/test_tasks_crud.py` | no module-level `regression` on smoke tests; smoke 4 + regression 48 = 52 |
| README commands and cleanup | `README.md` | exact `pytest -m smoke` and `pytest -m "regression and not smoke"` commands; no PhysioNet or 2026 Challenge text |
| Docker integration CI | `.github/workflows/ci.yml` | `docker-integration` job builds image, waits for health, runs `docker compose run --rm tests`, always cleans up |
| Repository metadata | GitHub CLI | exact description and 13 topics present |

## CI evidence

Workflow URL:
`https://github.com/yazanus94-dot/python-api-test-automation-framework/actions/runs/45261579388`

Result: `conclusion: success`, `headSha: 039d081...`. Both jobs passed:
`quality-and-tests` and `docker-integration` (including image build, API
health wait, tests container against `http://api:8000`, and cleanup).

## How to reproduce

1. Open the commit link:
   `https://github.com/yazanus94-dot/python-api-test-automation-framework/commit/039d081ef3247eb04774fd28ac676c256bc6e627`
2. Open the Actions run link above and confirm both jobs are green.
3. Clone the repository and run `python -m pytest -v`, `ruff check .`,
   `ruff format --check .`, `mypy app qa_framework`.
