# Handoff-Notice-Audit Fields — current

Field schema for rev0062 report family.

Rows: 8

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| notice_check_id | yes | nonempty string | stable notice audit row id |
| check | yes | nonempty string | notice check key |
| file | yes | package-relative path | file checked |
| severity | yes | info/high | severity |
| status | yes | pass/fail | status |
| required_text | yes | regex or phrase | required warning language |
| observed | yes | free text | observed result |
| note | yes | free text | explanation |
