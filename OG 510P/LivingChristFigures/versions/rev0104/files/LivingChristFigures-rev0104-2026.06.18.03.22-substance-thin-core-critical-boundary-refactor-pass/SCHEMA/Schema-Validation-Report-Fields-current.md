# Schema Validation Report Fields current

Dedicated field schema for `SCHEMA/Schema-Validation-Report-current.csv`, added in rev0055 to close the rev0054 schema-coverage backlog.

| field | required | allowed/pattern | meaning |
|---|---:|---|---|
| severity | true | info/low/medium/high | Severity of the finding; high blocks release handoff unless explicitly exempted by the validator. |
| check | true | string; non-empty when semantically required | `check` column from `SCHEMA/Schema-Validation-Report-current.csv`; field schema added in rev0055 to close schema-coverage backlog. |
| file | true | package-relative path or pipe-delimited package-relative paths | Package-relative file path or file scope under audit. |
| detail | true | string; non-empty when semantically required | Human-readable detail for the finding or row. |
