# rev0030 refactor/audit notes

## Refactors

- Added `src/muc5/opening_counterfactual_repeat.py` to separate repeated branch rollouts from the original one-rollout counterfactual panel.
- Extended the counterfactual mulligan loader with `mulligan_repeated_counterfactual_ranker_rev0030` while preserving the rev0029 model name.
- Added no-choice segment fingerprint rows to `src/muc5/nochoice_segments.py` without changing normal public payoff semantics.
- Added `repeated_counterfactual_mulligan_gate_bundles(...)` so strategy sets own the rev0030 policy panel.

## Audit additions

The cube audit now checks:

```text
repeated opening counterfactual rows exist
C++ transition checks for branch rollouts have zero skipped events and zero mismatches
repeated counterfactual mulligan payoff passes promotion/statistical/replay/C++ gates
repeated counterfactual model loads under the correct public name
no-choice segment fingerprints exist and have start/end rows
required rev0030 docs/scripts/tests/data exist
```

## Caveat

The model pipeline is working better than the model signal. rev0030 deliberately archives the weak non-tie accuracy rather than hiding it.
