# Chrony capture and reference evaluator — rev0123

## Purpose

rev0123 keeps the rev0122 vertical slice but removes two safety gaps that were still too easy to miss:

```text
chronyc command transcript with wall-clock and monotonic brackets
    -> validated capture envelope
    -> typed ChronyObservation
    -> conservative interval and source posture
    -> P1-general-computing assessment
    -> machine-readable explanation
```

The capture envelope is adapter-local. It does **not** add a seventh TimeState field and it does **not** claim NTS verification, UTC traceability, or chrony configuration audit.

## New capture envelope

`tools/chrony_capture.py` records or validates `chrony_command_capture_v1` JSON. A usable capture contains:

- `chronyc -v` output;
- `chronyc -n tracking` output;
- `chronyc -n sources` output;
- collector wall-clock `wall_start`, `wall_end`, and `collected_at`;
- collector monotonic start/end nanosecond counters;
- per-command wall-clock and monotonic brackets;
- command exit status, timeout status, stdout, and stderr;
- unsupported/not-verified statements.

The validator rejects inverted wall-clock intervals, inverted monotonic intervals, command intervals outside the collector bracket, duplicate/missing command roles, unexpected command arguments, failed replay commands, and malformed timestamps.

The evaluator now accepts either raw replay text or a capture envelope:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tools/chrony_capture.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 tools/chrony_capture.py --validate tests/fixtures/chrony/capture-normal.json

PYTHONDONTWRITEBYTECODE=1 python3 tools/chrony_adapter.py \
  --capture tests/fixtures/chrony/capture-normal.json \
  --evaluated-at 2026-06-17T18:45:09.000000000Z \
  --output bundle
```

`--live` now routes through the capture envelope instead of directly reading command text. If `chronyc` is unavailable or a command exits nonzero, the capture may still be written by `tools/chrony_capture.py` for diagnosis, but the adapter will not treat failed command output as replay evidence.

## Conservative interval rule

The rev0122 formula was tightened because chrony-style root delay can be negative in unusual peer/path situations. A negative root delay must not shrink a safety interval. rev0123 therefore uses:

```text
abs(system_time_offset_seconds) + root_dispersion_seconds + 0.5 * max(root_delay_seconds, 0)
```

The replay/evaluation growth allowance remains:

```text
skew_ppm * max(0, evaluated_at - collected_at) / 1_000_000
```

The emitted interval is centered on `evaluated_at`; `collected_at` affects age and holdover growth. The sign of `System time` still does not narrow or shift the interval.

## P1 policy used by this evaluator

This is still a local reference policy, not a TimeSync-wide norm.

```text
satisfied/security_sensitive_time: bound <= 100 ms and replay age <= 300 s and usable source posture
fallback/coarse_logging:          bound <= 1000 ms and replay age <= 3600 s
fallback/display_time:            bound <= 5000 ms and replay age <= 86400 s
otherwise:                        unsatisfied/diagnostic_local_only
```

`Leap status` other than `Normal` or an unusable stratum fails closed to `unsatisfied`.

## Executable coverage

rev0123 adds:

- `tools/chrony_capture.py --self-test`;
- `tests/fixtures/chrony/capture-normal.json`;
- `CHRONY-P1-NEGATIVE-ROOT-DELAY-CONSERVATIVE` in `tests/chrony-adapter-golden.yaml`;
- `examples/chrony/tracking-negative-root-delay.txt`;
- `examples/evaluator/chrony-p1-negative-root-delay-conservative.json`;
- semantic vector `TV-123-001`.

## What this still does not prove

- NTS or symmetric-key verification;
- named UTC realization traceability;
- chrony configuration correctness;
- leap-smear policy discovery;
- application monotonic-clock behavior;
- PTP behavior;
- interoperability with non-chrony NTP implementations;
- production fitness of the P1 thresholds.

## Why this matters

The previous state could parse replay text, but a future live capture was still at risk of becoming an unstructured paste. rev0123 makes command collection itself testable and rejects evidence whose timing bracket or command success is incoherent. It also closes an arithmetic bug class where an unusual negative root delay could reduce the emitted uncertainty bound.
