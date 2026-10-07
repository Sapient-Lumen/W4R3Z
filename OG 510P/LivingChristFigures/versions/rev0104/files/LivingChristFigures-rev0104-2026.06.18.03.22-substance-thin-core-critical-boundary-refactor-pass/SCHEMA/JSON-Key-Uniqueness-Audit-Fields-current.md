# JSON-Key-Uniqueness-Audit Fields — current

| field | required | allowed_values_or_pattern | meaning |
|---|---|---|---|
| finding_id | yes | nonempty string | stable finding id |
| json_path | yes | nonempty string | package-relative JSON path |
| object_path | yes | nonempty string | object path inside JSON |
| duplicate_keys | yes | nonempty string | duplicate keys separated by | |
| severity | yes | info|high | info|high |
| status | yes | pass|fail | pass|fail |
| note | yes | nonempty string | review note |
