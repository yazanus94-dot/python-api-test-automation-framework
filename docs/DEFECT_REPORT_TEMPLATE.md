# Defect report template

Copy this block into an issue or QA hand-off. Replace every placeholder.

```markdown
## Summary
<one sentence: what is wrong>

## Environment
- Commit: <sha>
- Python: <version>
- API base URL: <url>
- Database: <isolated/test or other, never production credentials>

## Steps to reproduce
1. <request or fixture setup>
2. <exact command, e.g. python -m pytest tests/api/test_x.py::test_y>

## Expected
<status code, error code, response fields>

## Actual
<status code, response excerpt with secrets redacted>

## Evidence
- JUnit: reports/junit.xml
- HTML: reports/report.html
- Log: reports/api_test.log (redacted)
- Test ID: <TC-... from docs/TEST_CASES.md>

## Severity / priority
<blocker | major | minor> / <P0 | P1 | P2>

## Suspected component
<app router / schema / security / framework client / CI>
```

Attach redacted artifacts only — never attach `.env`, database files or tokens.
