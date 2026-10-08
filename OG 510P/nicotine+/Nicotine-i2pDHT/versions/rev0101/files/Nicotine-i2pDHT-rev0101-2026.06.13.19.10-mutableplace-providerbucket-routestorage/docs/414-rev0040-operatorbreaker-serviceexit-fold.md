# rev0040 — operatorbreaker-serviceexit-fold

rev0040 stays in the DHT/garden-service control plane and attacks a dangerous seam: operator control after service continuity exists.

The new rule is:

```text
A local operator action is not an escape hatch; it is another signed, scoped, replayable claim.
```

New surfaces:

- `operatorintent`: scoped, signed local operator intent capsules for pause, resume, demotion, bridge disable, maintenance, and emergency freeze.
- `servicebreaker`: a local circuit-breaker lane for false service, hard negatives, active withdrawal, overload, refusal-only loops, and diverse recovery.
- `serviceexit`: the joined boundary that decides whether a service may pause, demote to leaf, disable bridge exposure, freeze, or resume.
- `operationsfold`: audit/refactor visibility for the rev0040 path.

The design pressure is that a garden node should be generous, but it must be able to stop safely. Unsafe stop/resume paths can erase hard negatives, strand tickets, keep stale public bridge exposure alive, or let a single local success turn into a broader side effect.
