# RFC 9249 crosswalk guard — rev0124

## Purpose

FT-0121 says not to generalize the chrony observation vocabulary until it has been compared with an NTP standards management surface. rev0124 adds that comparison as a guardrail, not as a new registry.

## Result

`tests/rfc9249-chrony-observation-crosswalk.yaml` maps or classifies current chrony observation fields against RFC 9249 NTP operational state. Fields such as stratum, reference ID, clock offset, root delay, root dispersion, and reference time have direct or partial comparison points. Chrony leap-status text, skew estimator uncertainty, source-selection symbols, and capture monotonic anchors do not become generic NTP state.

## Guard rule

Every row currently carries:

```text
core_promotion: forbidden
```

That means the six-field TimeState core cannot grow merely because the chrony adapter needed implementation-specific evidence. A later release may change this only after another real adapter proves an irreducible cross-implementation need.


## rev0129 update

`tools/rfc9249_crosswalk.py` now validates both `tests/rfc9249-chrony-observation-crosswalk.yaml` and `tests/rfc9249-ntpq-observation-crosswalk.yaml`. The purpose remains unchanged: adapter observation fields can be compared to RFC 9249 operational-state leaves, but they remain forbidden for TimeState core promotion until a later adapter proof demonstrates an irreducible semantic gap.
