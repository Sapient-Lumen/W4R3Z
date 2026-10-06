# Verified lazy tree mount / materialization / evidence boundary

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, isolation, operability
**Patterns:** Adapter→Shadow→Replace, Plan→Apply→Receipt

`docs/299-verified-lazy-rootfs-and-on-demand-mounts.md` captured the attractive lesson: verified lazy pulling can remove a lot of cold-start waste.
This doc makes the harder architectural cut:
**lazy tree mounts are a transport/projection lane, not a new source of deployment authority, and their evidence defaults must stay privacy-bounded.**

See also:
- ADR: `adrs/ADR-0117-verified-lazy-tree-mount-materialization-and-evidence-boundary.md`
- lazy-mount lesson doc: `docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`
- store/image distribution lessons: `docs/119-casync-cvmfs-distribution.md`
- observability as capability: `docs/192-observability-as-capability.md`
- explicit runtime views: `docs/264-mount-namespaces-and-union-views.md`
- lazy-mount contract shapes: `spec/tree.mount.plan.schema.json`, `spec/tree.mount.receipt.schema.json`

## Why this needs a hard decision

Without a narrow contract, lazy pulling creates three kinds of drift at once:

- the transport path starts pretending to be deployment authority,
- fetch traces become a de-facto ambient observability feed,
- and unsupported backends silently fall back to full materialization without a review surface.

That is exactly the kind of convenience drift DeriveBSD is trying to avoid.
A–D may all want the optimization, but they do **not** all want the same privacy posture, failure posture, or backend assumptions.

## Accepted boundary

Across all profiles:

- the authoritative runtime/deployment identity remains the reviewed tree digest and the higher-level object that requested it (`mount.view`, `closure.manifest`, `runtime.manifest`, `base.set`, etc.),
- `tree.mount.plan` is the authoritative **projection/transport execution plan**, not a replacement for those reviewed objects,
- `tree.mount.receipt` is bounded execution evidence for that plan,
- and path-level fetch traces are **not** the default evidence surface.

The plan must now make three choices explicit:

1. **projection mode**
   - `materialize`
   - `prefetch`
   - `lazy`

2. **fallback policy**
   - `fail_closed`
   - `materialize`
   - `prefetch`

3. **fetch evidence scope**
   - `digest-only` (default-worthy)
   - `path-level` (stronger, explicit, and not ambient)

This is the real design cut.
DeriveBSD is not deciding one universal lazy backend or one universal privacy posture.
It is deciding that these choices must be reviewable *before* rollout and receipted *after* execution.

## Canonical source-of-truth rule

A lazy mount does not get to redefine what was intended to run.
The requesting reviewed object stays upstream of the transport lane.

For `tree.mount.plan`, that means:

- `authority_binding` may point back to the reviewed object digests that requested the projection,
- `projection.mode` states whether bytes are materialized, prefetched, or fetched on demand,
- `projection.fallback_policy` states whether a node may switch posture when the preferred backend is unavailable,
- `projection.fetch_evidence_scope` states whether ordinary evidence is summary-only or path-revealing,
- and `projection.constraints` states which backend capabilities are required so planners do not quietly assume support that is not there.

For `tree.mount.receipt`, that means:

- the receipt records the **realized** mode,
- whether fallback actually happened,
- whether constraints were satisfied,
- and any stronger fetch-trace object is an explicit optional join rather than a hidden default side channel.

## Privacy + evidence posture

The archive now fixes the default evidence stance:

- ordinary lazy-mount evidence is **digest/summary level**,
- byte counts and cache-hit style counters are acceptable,
- path-level fetch traces are a stronger debugging/forensics lane,
- and those stronger traces should be gated the same way other observability powers are gated: explicitly, narrowly, and revocably.

This keeps “what files were faulted in?” from becoming ambient workplace surveillance or an unreviewed exfiltration surface.

## Product-shape fit

- **A / fleet host:** lazy projection may be useful for rollout speed, but default evidence should remain `digest-only` and fallback should usually stay `fail_closed` or a predeclared materialization path.
- **B / workstation:** lazy mounts can buy real responsiveness, but stronger path-level tracing belongs in explicit support/debug lanes rather than normal app telemetry.
- **C / general OS:** all three modes can stay viable, but the chosen posture must still be explicit and receipted rather than hidden in backend magic.
- **D / appliance / regulatory:** lazy projection may still be useful for staging/factory workflows, but production posture should strongly prefer declared mirror/materialization behavior and narrow evidence exports.

## Minimal v0 spec worth implementing

The smallest useful contract is now explicit in the existing typed artifacts:

- `spec/tree.mount.plan.schema.json`
- `spec/tree.mount.receipt.schema.json`
- `spec/examples/tree.mount.plan.json`
- `spec/examples/tree.mount.receipt.json`

The important point is not “support every backend.”
It is that every backend now has to show its work on the same typed surface:

- which reviewed object requested the projection,
- which execution mode was intended,
- which downgrade path was allowed,
- which privacy/evidence scope was allowed,
- and what actually happened.

## Why this is the right small hard decision

This boundary preserves the optimization without letting it become folklore authority.
It also avoids a false binary between “always lazy” and “never lazy.”
DeriveBSD can now keep materialize/prefetch/lazy as first-class reviewable postures while keeping the deployment identity, evidence posture, and fallback semantics coherent across A–D.

Last updated: 2026-03-16r256
