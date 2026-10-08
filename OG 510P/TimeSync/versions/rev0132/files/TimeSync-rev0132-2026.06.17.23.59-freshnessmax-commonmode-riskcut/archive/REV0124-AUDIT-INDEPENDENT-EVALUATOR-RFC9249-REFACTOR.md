# rev0124 focused refactor audit — independent evaluator and RFC 9249 guard

## Refactor target

The chrony slice had one adapter/evaluator implementation. That left a risk that tests would confirm only the implementation's own assumptions. rev0124 adds a second evaluator over the typed observation boundary.

## Independence boundary

`tools/chrony_observation_eval.py` consumes `chrony_observation` JSON and does not import `tools/chrony_adapter.py`. It shares only the project-level exact RFC 3339 parser and profile catalog. This is enough independence to catch evaluator arithmetic and decision regressions while keeping chronyc text parsing in the primary adapter.

## RFC 9249 audit result

The crosswalk shows that several chrony fields correspond to RFC 9249 NTP operational-state nodes, including stratum, refid, clock offset, root delay, root dispersion, and reference time. It also shows gaps: chronyc leap-status text, skew estimator uncertainty, source-selection symbols, and local capture monotonic anchors are not generic NTP state. Those remain adapter evidence and are forbidden from core promotion in this release.

## Waste reduced

Runtime-generated policy references and capture-version fields now come from `REVISION-RECEIPT.json`. This removes a repeated manual edit surface without weakening release integrity.

## Remaining risk

This is still a replay/cross-check proof, not a live-host proof. The next high-value step remains running `tools/chrony_capture.py` on a machine with chronyd/chronyc available and retaining the real capture envelope.
