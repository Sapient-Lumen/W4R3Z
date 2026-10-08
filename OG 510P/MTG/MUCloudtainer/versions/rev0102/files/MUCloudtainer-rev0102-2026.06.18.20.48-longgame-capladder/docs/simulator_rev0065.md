# rev0065 simulator note

rev0065 is a policy-response and claim-quarantine revision.  It does not change gameplay semantics, card definitions, legal-action generation, hidden-information exposure, mulligan semantics, terminal loss rules, C++ transition logic, or replay semantics.

Runtime changes are limited to:

```text
src/muc5/public_agents.py      # new public counter_guard profile
src/muc5/counter_response.py   # reusable response/quarantine experiment helpers
```

Validation:

```text
pytest: 223 passed
smoke: passed
inherited audit: passed, 176 checks
counter-response gate: passed
C++ chosen transition mismatches/skips: 0 / 0
```
