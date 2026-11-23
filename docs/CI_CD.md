# CI/CD

## Workflow

`.github/workflows/ci.yml` runs on push to `main`, pull requests to `main` and
manual dispatch. It uses Python 3.12 and least-privilege `permissions: contents: read`.

Order:

1. `pip install -r requirements.txt -r requirements-dev.txt`
2. `ruff check .`
3. `ruff format --check .`
4. `mypy app qa_framework`
5. `python -m pytest -m smoke -v`
6. `python -m pytest -m regression -v`
7. Upload `reports/` with `if: always()` — HTML and JUnit survive failures.

Actions used: `actions/checkout@v4`, `actions/setup-python@v5`,
`actions/upload-artifact@v4`.

## Local equivalent

```powershell
.\scripts\quality-checks.ps1
```

or individually:

```powershell
ruff check .
ruff format --check .
mypy app qa_framework
python -m pytest -m smoke -v
python -m pytest -m regression -v
```

## Secrets

No CI secret is required: the test fixture uses a temporary SQLite database and
a test-only JWT secret. Production deployments must supply `JWT_SECRET_KEY`
through their secret manager; `.env` is git-ignored and never uploaded as an
artifact.
