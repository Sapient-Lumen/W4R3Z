# TimeSync rev0132 validation report

Validation target: multiple local assessed states must not be cherry-picked, freshness must not be understated, and common-mode/source-diversity posture must not be upgraded by interval overlap. rev0132 keeps rev0131's intersection/union behavior but adds stalest-input freshness and same-root/common-mode regression checks.

## New executable checks

- `tools/multisource_adjudicator.py --self-test`
- `tests/multisource-adjudication.yaml`
- `TV-132-001` generated semantic-vector example

## Expected validation output

```text
TimeSync rev0132 validation passed.
Validated 374 semantic vectors, 6 profile maps, 6 transport adapters, and 25 evidence classes.
```

## Additional retained checks

```text
TimeSync chrony capture self-test passed.
TimeSync chrony adapter/evaluator self-test passed.
TimeSync independent chrony observation evaluator self-test passed.
TimeSync ntpq adapter/evaluator self-test passed.
TimeSync adapter equivalence self-test passed.
TimeSync shared NTP bound self-test passed.
TimeSync chrony P1 policy self-test passed.
TimeSync profile-decision acceptance tests passed.
TimeSync RFC 9249 adapter-observation crosswalks passed.
TimeSync multi-source adjudication self-test passed.
```
