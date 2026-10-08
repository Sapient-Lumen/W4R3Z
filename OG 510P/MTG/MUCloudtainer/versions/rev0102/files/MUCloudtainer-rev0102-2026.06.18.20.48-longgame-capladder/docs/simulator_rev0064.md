# rev0064 simulator note

rev0064 is a claim-gate and diagnostic revision.  It does not change gameplay semantics, cards, legal-action generation, hidden-information exposure, mulligan semantics, terminal loss rules, or C++ transition logic.

The only new runtime code is the reusable `closure_vs_counter` experiment layer and tests around its matched-policy construction/comparison helpers.

Validation:

```text
pytest: 214 passed
smoke: passed
inherited audit: passed, 176 checks
closure-vs-counter gate: passed
C++ chosen transition mismatches/skips: 0 / 0
```
