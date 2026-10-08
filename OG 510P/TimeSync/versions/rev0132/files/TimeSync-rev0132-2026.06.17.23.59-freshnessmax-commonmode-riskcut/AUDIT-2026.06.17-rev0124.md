# TimeSync rev0124 audit — independent comparison and fallback-lane hardening

## Risk cut chosen

rev0123 made chrony replay/capture evidence evaluable, but it still had a monoculture risk: the only evaluator was the same implementation that generated the examples and golden outputs. rev0124 targets that risk directly rather than adding another registry.

## Substantive changes

- Added `tools/chrony_observation_eval.py`, an independent evaluator over typed `chrony_observation` JSON.
- The independent evaluator does **not** import `tools/chrony_adapter.py`; its self-test rejects direct code imports from the primary adapter.
- The independent evaluator recomputes exact interval endpoints, chrony bound arithmetic, source posture, profile decision, policy acceptance, and key explanation fields for every successful chrony golden case.
- Added `CHRONY-P1-DISPLAY-HOLDOVER-FALLBACK`, which exercises the display-only fallback lane that rev0122/rev0123 left untested.
- Added `examples/evaluator/chrony-p1-display-holdover-fallback.json` and semantic vector `TV-124-001`.
- Added `tests/rfc9249-chrony-observation-crosswalk.yaml` and `tools/rfc9249_crosswalk.py` to compare current chrony observation fields with RFC 9249 operational-state surfaces before generalizing an observation vocabulary.
- Made chrony capture/evaluator policy strings derive from `REVISION-RECEIPT.json`, reducing repeated hard-coded revision churn in generated examples.

## What this catches now

A future edit that changes the primary evaluator's interval centering, root-delay clamp, holdover growth, fallback thresholds, or source posture logic should now fail against an independently computed result. A future attempt to smuggle chrony-specific fields into the TimeState core should also fail the RFC 9249 crosswalk guard unless a later adapter proof explicitly changes that rule.

## Refactor/audit result

The main waste corrected here is duplicated revision bookkeeping inside runtime tools. The tools now read the release identity from the receipt for policy-reference strings and capture-version stamps. This keeps the release identity fix from rev0121 alive without requiring hand edits in generated chrony examples each turn.

## Still intentionally not closed

FT-0121 remains open. The live capture path is implemented but not exercised in this cloud container; no NTS or symmetric-key verification is performed; named UTC realization remains unproven; leap-smear policy discovery is absent; and PTP/non-chrony comparison is still future work.
