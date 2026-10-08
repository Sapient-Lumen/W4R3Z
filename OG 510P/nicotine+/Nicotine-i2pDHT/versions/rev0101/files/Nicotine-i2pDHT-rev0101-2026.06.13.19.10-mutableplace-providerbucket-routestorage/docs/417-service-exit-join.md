# Service exit join

`serviceexit.py` joins operator intent, breaker pressure, service drain, continuity-journal memory, and profile-GC preservation before service side effects.

Current accepted exits:

```text
pause service        -> accepted operator intent + open breaker + continuity memory
demote to leaf       -> accepted operator intent + clean drain + continuity memory + profile GC
public bridge disable -> accepted operator intent + clean drain + continuity memory
emergency freeze     -> accepted operator intent as local hold
resume service       -> accepted operator intent + closed/half-open breaker + no accepted drain conflict
```

The exit gate rejects quarantined signals, replay, service/scope/request drift, action mismatch, and hard-negative drop. A clean-looking drain cannot erase tombstones, revocations, key-crisis notices, provider-false evidence, or witness-fork evidence.
