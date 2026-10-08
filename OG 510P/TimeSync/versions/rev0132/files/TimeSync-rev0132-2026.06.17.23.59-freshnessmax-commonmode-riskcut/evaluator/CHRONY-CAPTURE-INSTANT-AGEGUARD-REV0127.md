# Chrony capture instant age guard — rev0127

## Problem

The chrony evaluator grows uncertainty from the age of the observation. In a command transcript, `chronyc -n tracking` supplies the offset, root dispersion, root delay, and skew used in that calculation. Later commands such as `sources` and `sourcestats` provide context, but they do not refresh the tracking bound.

If replay uses the collector's final timestamp as the tracking observation time, a transcript can appear younger merely because diagnostic commands ran after `tracking`. That can make the interval too narrow.

## Rule

For `chronyc-command-transcript-v1` replay:

```text
replay collected_at = commands[role == tracking].start_wall
```

The collector final timestamp is retained as `capture_context.collector_collected_at`. It is not used to reduce replay age.

## Test

`CHRONY-P1-CAPTURE-TRACKING-INSTANT-AGE-GUARD` uses a fixture where:

- tracking starts at `2026-06-17T18:45:08.000000000Z`;
- the collector finishes at `2026-06-17T18:45:18.000000000Z`;
- evaluation occurs at `2026-06-17T18:50:08.000000000Z`.

The expected age is exactly `300` seconds. A rev0126-style collector-final replay would have produced `290` seconds and a narrower interval.

## Boundary

This guard is not cryptographic verification, named UTC traceability, leap-smear discovery, or proof of real host synchronization. It is an executable replay-conservatism guard inside the chrony adapter boundary.
