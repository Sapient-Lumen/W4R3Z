# Required Document Coverage Fields current

Field contract for the matching current table.

| field | required | allowed_values_or_pattern | meaning |
|---|---|---|---|
| `finding_id` | true | ^rdc_[0-9]{4}$ | Stable finding identifier emitted by required_document_coverage.py. |
| `severity` | true | info/medium/high | Finding severity; high blocks handoff. |
| `check` | true | non-empty string | Name of required-document check. |
| `file` | true | package-relative path or directory | File/path being checked. |
| `row` | true | integer or 0 | CSV row number where applicable; 0 for file-level checks. |
| `status` | true | pass/missing/missing_current_revision/drift/missing_companion | Machine-readable coverage status. |
| `detail` | true | non-empty string | Finding detail. |
| `remediation` | true | non-empty string | Expected correction if status is not pass. |
