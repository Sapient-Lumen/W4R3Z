# Field Schema Consistency Audit Fields current

Field schema for `META/Field-Schema-Consistency-Audit-current.csv`, added in rev0055.

| field | required | allowed/pattern | meaning |
|---|---:|---|---|
| finding_id | true | ^fsca_[0-9]{4}$ | Stable finding identifier emitted by field_schema_consistency.py. |
| severity | true | info/medium/high | Finding severity; high blocks release handoff. |
| check | true | non-empty string | Name of field-schema consistency check. |
| file | true | package-relative path | Field schema file or target table being checked. |
| row | true | integer or 0 | Row number when applicable; 0 for file-level checks. |
| detail | true | non-empty string | Explanation of the finding or pass row. |
| field_schema_status | true | pass/schema_only_no_exact_table/missing_companion/header_mismatch/duplicate_field/missing_field/extra_field/invalid_schema | Machine-readable status for the field-schema coverage/consistency check. |
