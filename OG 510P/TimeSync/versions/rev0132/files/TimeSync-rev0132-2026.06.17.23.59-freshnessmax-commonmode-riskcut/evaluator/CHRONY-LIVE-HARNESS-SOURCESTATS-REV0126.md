# Chrony live harness and sourcestats capture — rev0126

## Risk selected

After rev0125, the chrony path had a policy artifact and independent evaluator, but the live path was still mostly unexercised in this cloud container. The capture helper could call `chronyc`, yet tests only proved deterministic, hand-built envelopes.

The other gap was frontier scope drift: FT-0121 explicitly called for tracking/sources/sourcestats capture, but the release only retained tracking and sources. That left estimator diagnostics outside the vertical slice and made future live-capture work likely to grow another ad hoc parser later.

## What changed

- `tools/chrony_capture.py` now captures `chronyc -n sourcestats` in addition to `chronyc -v`, `chronyc -n tracking`, and `chronyc -n sources`.
- `tools/chrony_capture.py --self-test` creates a temporary fake `chronyc` executable and runs the real subprocess-based live path against it.
- `tools/chrony_adapter.py` parses sourcestats rows into `sourcestats_summary` with sample count, residual runs, span, frequency, frequency skew, offset, and standard deviation.
- `tests/fixtures/chrony/observation-sourcestats-normal.json` shows the adapter-local observation shape.
- `tests/chrony-adapter-golden.yaml` adds `CHRONY-P1-SOURCESTATS-DIAGNOSTIC-CAPTURED`.
- The RFC 9249 crosswalk now classifies sourcestats estimator fields as gaps/adapter-local and forbids core promotion.

## Design boundary

Sourcestats is intentionally not used to authorize P1. The P1 interval remains based on the chrony tracking bound and skew growth. Sourcestats is retained because it helps audit chronyd estimator quality and future capture forensics, but rev0126 does not silently convert it into a stronger TimeState.

## What remains unproven

The fake-live harness proves the command-runner path, envelope validation, replay extraction, and parser plumbing. It does not prove the host's clock, chronyd state, NTS authentication, named UTC realization, leap-smear policy, or interoperability with non-chrony implementations. FT-0121 therefore remains open.
