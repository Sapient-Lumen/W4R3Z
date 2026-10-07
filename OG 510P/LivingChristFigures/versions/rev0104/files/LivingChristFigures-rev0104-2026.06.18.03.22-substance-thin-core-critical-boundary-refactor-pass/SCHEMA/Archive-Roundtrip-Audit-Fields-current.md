# Archive-Roundtrip-Audit-Fields-current — current

Updated by rev0086 to match `tools/archive_roundtrip_audit.py` output after compression-sanity hardening.

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| check | yes | nonempty string unless explicitly blank | archive roundtrip check key |
| severity | yes | info|high | severity of the roundtrip finding |
| status | yes | pass|fail | result of the archive roundtrip check |
| observed_value | yes | nonempty string unless explicitly blank | measured value used by the check |
| detail | yes | nonempty string unless explicitly blank | human-readable detail and remediation context |
