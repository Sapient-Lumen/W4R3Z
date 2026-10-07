# Public Release Lint Fields — current

Field contract for `META/Public-Release-Lint-current.*`.

Rows: 8

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| finding_id | true | unique prl_ id | Finding row id. |
| severity | true | info/medium/high | High blocks public handoff; medium is review reminder. |
| risk_type | true | controlled by tool | Configured public-layer lint category. |
| file | true | PUBLIC/* path | Public file scanned. |
| line | true | integer-like | Line number; 0 for file-level pass rows. |
| match | false | short string | Matched text or empty for pass rows. |
| release_effect | true | non-empty string | Handoff consequence. |
| remediation | true | non-empty string | Required action or review note. |
