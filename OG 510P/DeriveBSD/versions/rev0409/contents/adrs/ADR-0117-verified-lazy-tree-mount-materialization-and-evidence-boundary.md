# ADR-0117: Verified lazy tree mounts are transport/projection plans, not deployment authority

- **Status:** Accepted
- **Date:** 2026-03-16
- **Deciders:** DeriveBSD archive maintainers

## Context

Open question 29 in `docs/266-open-questions-and-risk-register.md` kept one expensive ambiguity alive:
should verified lazy pulling be treated as just another optional transport optimization, or should it quietly become a new authority/evidence surface for what runs on the machine?

The archive already had the useful pieces:

- `docs/299-verified-lazy-rootfs-and-on-demand-mounts.md` captured the composefs/eStargz/Nydus lesson,
- `spec/tree.mount.plan.schema.json` and `spec/tree.mount.receipt.schema.json` existed as early typed shapes,
- `docs/152-store-view-minimization.md` and `docs/264-mount-namespaces-and-union-views.md` already assumed reviewed runtime views should stay explicit,
- and `docs/192-observability-as-capability.md` already implied that access-pattern observability should not become ambient.

But the critical boundary was still fuzzy.
If we leave it fuzzy, three bad things happen:

1. transport state starts pretending to be deployment identity,
2. lazy-fetch traces become ambient telemetry by accident,
3. and unsupported nodes silently change privacy/performance posture through hidden fallback.

That would make a valuable optimization too expensive to trust.

## Decision

DeriveBSD now fixes the lazy-mount boundary as follows:

1. **Reviewed deployment identity stays upstream of the transport lane.**
   The authoritative object remains the reviewed tree digest and the higher-level object that requested it (`mount.view`, `closure.manifest`, `runtime.manifest`, `base.set`, etc.).

2. **`tree.mount.plan` is the authoritative execution plan for the projection lane.**
   It specifies how the tree will be satisfied, but it does not replace the reviewed object that named the tree.

3. **`tree.mount.receipt` is bounded evidence, not an ambient trace feed.**
   Ordinary receipts summarize realized mode, fallback, constraint satisfaction, and compact counters/digests. Path-level fetch traces are an explicit stronger lane, not the default.

4. **Projection posture must be explicit.**
   The plan must name:
   - `materialize` vs `prefetch` vs `lazy`,
   - explicit fallback policy (`fail_closed`, `materialize`, `prefetch`),
   - explicit fetch-evidence scope (`digest-only`, `path-level`),
   - and explicit backend constraints needed for the chosen posture.

## Consequences

### Positive

- Lazy pulling stays available as a high-leverage optimization without silently becoming deployment authority.
- A–D can pick different privacy/performance defaults without forking the artifact model.
- Receipts remain useful for forensics and review without normalizing access-pattern surveillance.
- Unsupported backends stop causing silent posture drift because fallback becomes a typed review surface.

### Trade-offs

- Backends now have to expose their capability requirements and downgrade behavior honestly.
- Implementations that want path-level fetch telemetry must do the extra work to wire it through explicit debug/observability lanes rather than hiding it in ordinary receipts.
- Some “it just works” backend magic is intentionally rejected because it would be too hard to reason about later.

## What this does not decide

This ADR does **not** decide:

- the single best lazy backend for DeriveBSD,
- exact planner heuristics for when `prefetch` beats `lazy`,
- exact cache-retention budgets per product line,
- or the final path-level tracing artifact shape for stronger debugging lanes.

It only fixes the coherence boundary: lazy tree mounts are a typed projection/transport lane with explicit posture and bounded evidence, not a hidden new authority surface.
