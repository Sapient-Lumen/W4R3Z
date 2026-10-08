# ntpq reference evaluator — rev0129

rev0129 adds a minimal second adapter for `ntpq -c rv` system variables plus `ntpq -pn` peer billboard text.

## Evidence boundary

The adapter emits `ntpq_observation` with:

- system fields from readvar: leap, stratum, refid, reftime, rootdelay, rootdisp, offset, and clk_wander;
- peer summary from the billboard: selected `*` / `o`, combined `+`, and other tally rows;
- authentication posture fixed to not observed / not verified.

## Conservative bound

The evaluator converts ntpq display milliseconds to seconds and computes:

```text
abs(offset_seconds) + root_dispersion_seconds + 0.5 * max(root_delay_seconds, 0) + clk_wander_ppm * age_seconds / 1_000_000
```

The offset sign is not used to narrow the interval. Negative root delay, if observed in a future fixture, cannot shrink the safety interval.

## Fail-closed behavior

- `leap != 00` or unusable stratum fails closed.
- Excessive bound or age yields diagnostic-only unsatisfied output.
- Missing root delay, root dispersion, offset, stratum, leap, refid, reftime, or clk_wander is rejected.
- `ntpq` output never strengthens authentication or traceability posture.

## Scope

This is a second operational-state comparison, not a full ntpd/NTPsec interoperability proof. It validates one common replay surface and keeps ntpq-specific facts outside the six-field TimeState core.
