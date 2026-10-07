# Current-Surface-Registry Fields — current

Field schema for rev0062 report family.

Rows: 10

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| surface_id | yes | nonempty string | surface row id |
| surface_path | yes | package-relative path or . | current CSV path |
| package_zone | yes | root/meta/schema/governance/public/package | package zone |
| surface_role | yes | controlled-ish role string | surface classification |
| generator_or_owner | no | tool path or owner | generator or owner |
| schema_path | no | SCHEMA/*-Fields-current.csv | field schema when present |
| row_count | yes | integer | row count |
| severity | yes | info/high | severity |
| status | yes | pass/fail | status |
| note | yes | free text | explanation |
