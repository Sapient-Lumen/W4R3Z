# Cross Report Reference Audit Fields — current

Generated/maintained for current schema coverage.

Field schema for `Cross-Report-Reference-Audit-current.csv`.

Rows: 7

| field | required | allowed_values_or_pattern | meaning |
|---|---|---|---|
| reference_check_id | yes | ref_NNNN | Stable row id. |
| file | yes | package-relative path or . | File/scope checked. |
| check | yes | slug | Reference check name. |
| severity | yes | info/medium/high | Severity. |
| status | yes | pass/fail | Check status. |
| observed | yes | free text | Observed stale/current-reference signal. |
| detail | yes | free text | Explanation. |
