# Selftest-Coverage-Matrix Fields — current

Rows: 7

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| coverage_id | true | selftest_cov_[0-9]{3} | Stable selftest coverage row identifier. |
| gate_id | true | gate_[0-9]{3} | Release gate identifier covered by one or more controlled mutations. |
| gate_name | true | nonempty string | Release gate name. |
| covered_by_selftest | true | yes/no | Whether all listed selftests passed. |
| selftest_ids | true | pipe-separated selftest IDs | Controlled-mutation selftests mapped to the gate. |
| coverage_status | true | pass/fail | Pass when mapped selftests exist and pass. |
| note | false | free text | Human-readable coverage rationale or missing-test note. |
