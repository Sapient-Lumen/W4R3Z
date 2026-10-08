# NTP adapter equivalence — rev0130

rev0130 adds a cross-adapter executable guard rather than a new core vocabulary.

## Problem

rev0129 added an ntpq adapter, but chrony and ntpq still carried separate copies of the same NTP-family bound arithmetic. That is risky because a future edit could make one adapter more permissive than the other for equivalent operational-state evidence.

## Change

`tools/ntp_bound.py` now owns the shared arithmetic:

```text
abs(system_time_offset_seconds)
+ root_dispersion_seconds
+ 0.5 * max(root_delay_seconds, 0)
+ abs(rate_error_ppm) * age_seconds / 1_000_000
```

It also owns exact RFC 3339 age calculation and nanosecond interval endpoint generation.

`tools/adapter_equivalence.py` feeds equivalent chrony and ntpq replay fixtures through separate parsers and evaluators. The check compares interval endpoints, collection age, total bound, timescale, regime, source posture, applicability, profile conformance, actionability, policy status, and fallback mapping.

## Boundary kept narrow

The equivalence harness does not introduce a generic NTP observation schema. Chrony `tracking/sources` and ntpq `readvar/peers` remain adapter-local evidence. The shared layer starts only after each adapter has supplied the minimal bound inputs.

## Still unsupported

- live chronyd/ntpd/NTPsec capture from this cloud container;
- NTS, symmetric-key MAC, AEAD, cookie, or packet transcript verification;
- named UTC realization proof;
- leap-smear policy discovery;
- PTP operational-state comparison.
