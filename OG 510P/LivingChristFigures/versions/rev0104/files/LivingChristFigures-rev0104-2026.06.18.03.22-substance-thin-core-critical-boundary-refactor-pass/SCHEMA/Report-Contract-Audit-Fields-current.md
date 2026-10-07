# Report Contract Audit Fields — current

Field schema for rev0066 report-contract registry/audit surfaces.

Rows: 7

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| audit_id | yes | report_contract_audit_[0-9]{4} | audit row id |
| check | yes | controlled-ish check name | audit check |
| severity | yes | info/medium/high | severity |
| status | yes | pass/review/fail | audit status |
| surface_path | yes | package-relative path or . | subject surface |
| expected_path | no | package-relative path or expectation | expected companion/schema/owner |
| detail | yes | free text | finding detail |
