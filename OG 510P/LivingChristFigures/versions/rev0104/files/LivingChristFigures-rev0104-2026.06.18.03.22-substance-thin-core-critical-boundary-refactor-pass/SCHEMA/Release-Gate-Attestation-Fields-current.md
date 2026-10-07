# Release Gate Attestation Fields current — current

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| gate_id | true | gate_NNN | Gate id. |
| gate_name | true | controlled by tool | Gate name. |
| status | true | pass/fail | Gate status. |
| evidence_files | true | pipe-separated paths | Files used as gate evidence. |
| blocking_findings | false | short string | Number or description of blocking findings. |
| note | true | non-empty string | Gate explanation. |
