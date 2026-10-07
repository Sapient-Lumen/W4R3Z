# Archive-Build-Manifest Fields — current

Rows: 5

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| build_check_id | true | archive_[0-9]{3} | Stable archive-build check identifier. |
| check | true | nonempty string | Archive-build assumption or invariant being checked. |
| value | true | string/integer | Observed value for the check. |
| status | true | pass/fail | Pass when the archive-build invariant holds. |
| note | false | free text | Human-readable build or package note. |
