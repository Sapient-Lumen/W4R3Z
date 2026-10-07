# Path Reference Audit Fields current

Field contract for the matching current table.

| field | required | allowed_values_or_pattern | meaning |
|---|---|---|---|
| `finding_id` | true | ^pra_[0-9]{4}$ | Stable finding identifier emitted by path_reference_audit.py. |
| `severity` | true | info/medium/high | Finding severity; high blocks handoff. |
| `check` | true | non-empty string | Name of path-reference check. |
| `file` | true | package-relative path | File containing the reference or package-level pass row. |
| `row` | true | integer or 0 | Line number where the reference was found; 0 for package-level rows. |
| `reference` | false | package-relative path or glob | Original referenced path-like string. |
| `target_path` | false | package-relative path or glob | Normalized target path or glob checked. |
| `status` | true | pass/glob_matched/missing_reference/read_error | Machine-readable resolution status. |
| `detail` | true | non-empty string | Human-readable detail. |
