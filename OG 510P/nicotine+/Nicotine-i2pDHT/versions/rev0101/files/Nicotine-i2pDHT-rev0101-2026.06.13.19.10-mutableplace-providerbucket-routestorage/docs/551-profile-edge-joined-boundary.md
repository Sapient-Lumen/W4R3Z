# Profile edge joined boundary

`profileedge.py` adds one more exact-boundary gate after the no-network live adapter.

It joins:

```text
live adapter report
backpressure report
router canary report, when outbound is involved
ingress drain report, when inbound is involved
profile budget report
negative scan report
profile generation
service generation
edge budget
hard-negative count
```

The profile-edge capsule is signed, sequence-numbered, previous-linked, time-bounded, family-tagged, and path-family-tagged. It rejects hard-negative pressure, generation rollback, component digest drift, same-sequence forks, previous-link mismatch, profile/service/scope/request/payload drift, and edge-budget overflow.

The goal is to keep future live effects from quietly crossing profile, service, or request boundaries after all individual components passed.
