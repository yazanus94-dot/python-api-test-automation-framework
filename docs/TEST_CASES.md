# Test cases (52 automated scenarios)

Stable IDs below map one-to-one to collected pytest tests. Verified with
`python -m pytest --collect-only -q`: auth 8, CRUD 11, negative 8, boundary 8,
contract 13, unit 4 = **52**.

## Authentication — `tests/api/test_auth.py` (TC-A01–A08)

| ID | Scenario | Expected |
|---|---|---|
| TC-A01 | Valid login | 200, `access_token`, `token_type=bearer`, `expires_in>0` |
| TC-A02 | Invalid username | 401, code `invalid_credentials` |
| TC-A03 | Invalid password | 401, code `invalid_credentials` |
| TC-A04 | Missing credentials | 422, code `validation_error` |
| TC-A05 | Invalid token | 401, code `invalid_token` |
| TC-A06 | Expired token | 401, code `invalid_token` |
| TC-A07 | Missing Authorization header | 401, code `missing_token` |
| TC-A08 | Valid token on protected endpoint | 200 |

## CRUD and persistence — `tests/api/test_tasks_crud.py` (TC-C01–C11)

| ID | Scenario | Expected |
|---|---|---|
| TC-C01 | Create task | 201, full response fields |
| TC-C02 | Read task | 200, equals created resource |
| TC-C03 | List with pagination | 200, `items/total/page/page_size` |
| TC-C04 | Update task | 200, title/status changed, `updated_at` advanced |
| TC-C05 | Delete task | 204, later GET 404 |
| TC-C06 | GET nonexistent | 404 |
| TC-C07 | PATCH nonexistent | 404 |
| TC-C08 | DELETE nonexistent | 404 |
| TC-C09 | SQLite persistence | Row present with expected title/owner |
| TC-C10 | Other user cannot read a task | 403, code `forbidden` |
| TC-C11 | Users only see their own tasks | All items owned by current user |

## Negative — `tests/api/test_negative.py` (TC-N01–N08)

| ID | Scenario | Expected |
|---|---|---|
| TC-N01 | Invalid JSON | 422 |
| TC-N02 | Missing required field | 422 |
| TC-N03 | Incorrect data type | 422 |
| TC-N04 | Invalid status value | 422 |
| TC-N05 | Invalid identifier | 422 |
| TC-N06 | Unsupported PUT method | 405 |
| TC-N07 | Invalid page=0 | 422 |
| TC-N08 | Invalid page_size 0 and 101 | 422 |

## Boundary — `tests/api/test_boundary.py` (TC-B01–B08)

| ID | Scenario | Expected |
|---|---|---|
| TC-B01 | Title length 1 | 201 |
| TC-B02 | Empty title | 422 |
| TC-B03 | Blank title | 422 |
| TC-B04 | Title length 200 | 201 |
| TC-B05 | Title length 201 | 422 |
| TC-B06 | Description length 1000 | 201 |
| TC-B07 | Description length 1001 | 422 |
| TC-B08 | page_size=100 | 200 |

## Contract — `tests/contract/` (TC-CT01–CT13)

| ID | Scenario | Expected |
|---|---|---|
| TC-CT01 | `/openapi.json` available | 200, JSON |
| TC-CT02 | OpenAPI 3.x | Version starts with 3 |
| TC-CT03 | Expected endpoints declared | All four paths present |
| TC-CT04 | TaskCreate request schema | `title` required, maxLength 200 |
| TC-CT05 | TaskResponse required fields | id/title/status/owner/created_at |
| TC-CT06 | Health content type and fields | JSON, status+service |
| TC-CT07 | Error envelope | `detail` + `code` |
| TC-CT08 | Bearer security scheme | Declared in OpenAPI |
| TC-CT09 | Create response schema | Validates against OpenAPI schema |
| TC-CT10 | List response schema | Validates against OpenAPI schema |
| TC-CT11 | Status code contract | 201/200/200/204 |
| TC-CT12 | JSON content types | JSON on health/tasks/openapi |
| TC-CT13 | Status enum in schema | pending/in_progress/completed |

## Unit — `tests/unit/test_utilities.py` (TC-U01–U04)

| ID | Scenario | Expected |
|---|---|---|
| TC-U01 | Password hash roundtrip | Correct verifies, wrong fails |
| TC-U02 | JWT roundtrip and expiry | Subject recovered; expired rejected |
| TC-U03 | Redaction | No secret in log payload |
| TC-U04 | Unique payload factory | Independent payloads |
