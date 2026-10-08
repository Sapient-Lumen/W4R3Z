# Refactor audit — rev0069

## Fixed bug class

rev0068 fixed a severe missing-cell bug in the response matrix: absent threat rows could be coerced to score 0.0. rev0069 audits nearby comparison helpers and applies the same fail-closed rule to:

```text
compare_counter_response_by_life
compare_threat_response_by_life
compare_closure_vs_counter_by_life
compare_threat_closure_by_life
```

Incomplete comparison cells now emit null scores, a missing-axis list, and `provisional_read = incomplete_matrix` rather than a point-estimate label.

## New tests

`tests/test_rev0069_population_frontier.py` covers:

```text
counter-response missing policy fail-closed behavior
threat-response missing policy fail-closed behavior
zero-sum fictitious-play value sanity on matching pennies
population security complete/incomplete cell reporting
evidence-index candidate classification
evidence-index live-reference blocking
```

## Substantive refactor

`src/muc5/population_frontier.py` centralizes a reusable population-panel generator and a small deterministic zero-sum/fictitious-play diagnostic. It is deliberately lightweight: enough to stop the pairwise treadmill and expose security floors, not a claim that PSRO/CFR is complete.
