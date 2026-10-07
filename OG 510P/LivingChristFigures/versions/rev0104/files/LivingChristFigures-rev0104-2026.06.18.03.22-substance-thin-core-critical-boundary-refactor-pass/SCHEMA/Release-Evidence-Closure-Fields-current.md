# Release Evidence Closure Fields current

| field | required | allowed_values_or_pattern | meaning |
|---|---|---|---|
| closure_check_id | true | release_closure_[0-9]{3} | Stable release-evidence closure row identifier. |
| check | true | nonempty string | Closure invariant being checked. |
| severity | true | info|low|medium|high | Severity of the closure finding. |
| status | true | pass|review|fail | Pass when closure invariant is satisfied; fail when it blocks handoff; review for non-blocking inventory gaps. |
| scope | true | nonempty string | Release evidence surface or ledger being checked. |
| detail | false | free text | Human-readable closure result note. |
