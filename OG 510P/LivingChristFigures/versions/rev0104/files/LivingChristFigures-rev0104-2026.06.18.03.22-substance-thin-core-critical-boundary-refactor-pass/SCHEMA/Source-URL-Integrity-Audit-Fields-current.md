# Source URL Integrity Audit Fields — current

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| finding_id | yes | suia_#### | audit row id |
| source_id | yes | Source-Registry-current.csv source_id | source id |
| domain | yes | pass-through string | source domain |
| url | yes | http(s) URL | source URL under structural audit |
| check_name | yes | url_structural_integrity | check performed |
| severity | yes | info/high | severity |
| status | yes | pass/fail: ... | check result |
| recommended_action | yes | pass-through string | repair/quarantine guidance |
| note | yes | pass-through string | audit note |
