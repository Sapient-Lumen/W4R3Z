# Rule46 Scan Fields current

Dedicated field schema for `META/Rule46-Scan-current.csv`, added in rev0055 to close the rev0054 schema-coverage backlog.

| field | required | allowed/pattern | meaning |
|---|---:|---|---|
| severity | true | info/low/medium/high | Severity of the finding; high blocks release handoff unless explicitly exempted by the validator. |
| risk_type | true | string; non-empty when semantically required | `risk_type` column from `META/Rule46-Scan-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| file_path | true | package-relative path or pipe-delimited package-relative paths | `file_path` column from `META/Rule46-Scan-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| line | true | string; non-empty when semantically required | `line` column from `META/Rule46-Scan-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| match | true | string; non-empty when semantically required | `match` column from `META/Rule46-Scan-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| context | true | string; non-empty when semantically required | `context` column from `META/Rule46-Scan-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| note | true | string; non-empty when semantically required | `note` column from `META/Rule46-Scan-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
