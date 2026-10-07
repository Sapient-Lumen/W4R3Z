# Checksum Scope Audit Fields current

| field | required | allowed_values_or_pattern | meaning |
|---|---|---|---|
| scope_check_id | true | checksum_scope_[0-9]{3} | Stable checksum-scope audit row identifier. |
| check | true | nonempty string | Checksum-scope invariant being checked. |
| severity | true | info|low|medium|high | Severity of the finding if the invariant is not fully satisfied. |
| status | true | pass|review|fail | Pass when the scope check is satisfied; fail when it blocks handoff; review for non-blocking order issues. |
| expected_count | true | integer string | Expected count for the scope check. |
| observed_count | true | integer string | Observed count for the scope check. |
| detail | false | free text | Human-readable scope finding or pass note. |
