# RFC-0182: CHERI temporal revocation evidence (optional lane)

Status: Draft

## Problem

If DeriveBSD adopts an optional CHERI lane, some deployments may enable CHERI temporal safety mechanisms
(CHERIvoke/Cornucopia-style revocation epochs).

Operators will need to answer:
- “Is temporal revocation enabled for this process?”
- “What revocation policy/pace is configured?”
- “Did a revocation epoch coincide with a latency or crash event?”

## Goals

- Treat CHERI temporal revocation policy as an explainable, queryable setting.
- Avoid conflating pointer revocation with DeriveBSD’s authority revocation.

## Proposal

1) Add a small evidence object `cheri.runtime.policy` (future work) that records:
   - whether temporal revocation is enabled
   - the default policy and any overrides
   - epoch pacing configuration (if applicable)

2) Encourage supervisors to correlate:
   - revocation epochs (as events)
   - resource budget violations
   - crash artifacts

3) Update CHERI lane docs to explicitly distinguish:
   - pointer revocation (temporal safety)
   - authority revocation (leases via indirection)

References:
- `docs/250-cheri-temporal-revocation-and-indirection.md`
- `docs/163-cheri-capability-lane.md`
