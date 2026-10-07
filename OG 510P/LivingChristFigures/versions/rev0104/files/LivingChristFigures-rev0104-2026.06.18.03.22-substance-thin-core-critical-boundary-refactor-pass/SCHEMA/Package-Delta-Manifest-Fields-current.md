# Package Delta Manifest Fields — current

Generated/maintained for current schema coverage.

Field schema for `Package-Delta-Manifest-current.csv`.

Rows: 10

| field | required | allowed_values_or_pattern | meaning |
|---|---|---|---|
| delta_id | yes | delta_NNNN | Stable row id. |
| path | yes | package-relative path | Stable package path compared to previous release. |
| change_type | yes | added/modified/removed/unchanged | Delta class. |
| previous_sha256 | conditional | 64 lowercase hex or blank | Previous file digest. |
| current_sha256 | conditional | 64 lowercase hex or blank | Current file digest. |
| previous_size_bytes | conditional | integer or blank | Previous file size. |
| current_size_bytes | conditional | integer or blank | Current file size. |
| severity | yes | info/high | Finding severity. |
| status | yes | pass/fail | Row status. |
| note | yes | free text | Interpretation. |
