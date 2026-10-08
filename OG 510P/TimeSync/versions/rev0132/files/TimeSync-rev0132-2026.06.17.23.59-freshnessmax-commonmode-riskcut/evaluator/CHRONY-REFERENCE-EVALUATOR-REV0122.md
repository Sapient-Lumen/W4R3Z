# Chrony reference evaluator — rev0122

## Purpose

This is the first executable proof that TimeSync can ingest a real timing implementation surface and produce a conservative six-field TimeState plus one profile decision. It is deliberately narrower than the surrounding archive.

```text
chronyc tracking + optional chronyc sources
    -> ChronyObservation
    -> conservative interval and source posture
    -> P1-general-computing assessment
    -> machine-readable explanation
```

## Input contract

`tools/chrony_adapter.py` accepts the human-readable `chronyc -n tracking` output and, optionally, `chronyc -n sources` output. The bundled fixtures in `examples/chrony/` are sanitized replays, not claims about this cloud container's live clock.

Required `tracking` fields:

```text
Reference ID
Stratum
Ref time (UTC)
System time
Skew
Root delay
Root dispersion
Leap status
```

Optional parsed fields include `Last offset`, `RMS offset`, `Frequency`, `Residual freq`, and `Update interval`.

## Conservative interval rule

The base error bound is:

```text
abs(system_time_offset_seconds) + root_dispersion_seconds + 0.5 * root_delay_seconds
```

The replay/evaluation growth allowance is:

```text
skew_ppm * max(0, evaluated_at - collected_at) / 1_000_000
```

The emitted interval is centered on `evaluated_at`, not the original collection time. The sign of `System time` is deliberately not used to narrow or shift the interval. That wastes some precision but avoids pretending the adapter has proved more than it has.

## P1 policy used by this evaluator

This is a local reference policy, not a TimeSync-wide norm.

```text
satisfied/security_sensitive_time: bound <= 100 ms and replay age <= 300 s and usable source posture
fallback/coarse_logging:          bound <= 1000 ms and replay age <= 3600 s
fallback/display_time:            bound <= 5000 ms and replay age <= 86400 s
otherwise:                        unsatisfied/diagnostic_local_only
```

`Leap status` other than `Normal` or an unusable stratum fails closed to `unsatisfied`.

## CLI examples

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tools/chrony_adapter.py --self-test

PYTHONDONTWRITEBYTECODE=1 python3 tools/chrony_adapter.py \
  --tracking examples/chrony/tracking-normal.txt \
  --sources examples/chrony/sources-normal.txt \
  --collected-at 2026-06-17T18:45:08.000000000Z \
  --evaluated-at 2026-06-17T18:45:09.000000000Z \
  --output bundle
```

`--live` exists and runs `chronyc -n tracking` and `chronyc -n sources` locally when chrony is installed, but rev0122 validation uses replay fixtures for reproducibility.

## What this does not prove

- named UTC realization traceability;
- NTS or symmetric-key verification;
- leap-smear policy discovery;
- application monotonic-clock behavior;
- PTP behavior;
- interoperability with non-chrony NTP implementations;
- production fitness of the P1 thresholds.

## Why this matters

This replaces a major false-comfort gap. Before rev0122, the archive could validate many TimeSync-native objects but could not show a real timing implementation surface becoming a TimeState. Now there is a small, testable path that can be extended or falsified without adding a new registry.
