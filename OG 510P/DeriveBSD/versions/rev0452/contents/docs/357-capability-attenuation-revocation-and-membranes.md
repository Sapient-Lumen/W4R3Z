# Capability attenuation, revocation, and membranes (make authority engineering mechanical)

DeriveBSD leans hard on object-capability ideas: **authority = possession of an unforgeable handle**.
That posture only works long-term if the ecosystem has a **small, repeatable vocabulary** for:

- **attenuation** (give a weaker handle than the one you hold)
- **revocation** (make previously granted authority stop working)
- **deep attenuation** (control what *new* authority can be obtained through a handle)

This doc is the style guide for doing that without re-inventing bespoke “permission flags.”

## Non-goals

- Replacing Capsicum/jails/portals: those are the concrete mechanisms.
- Solving all distributed capability problems (see CapTP/OCapN lane).

## Core patterns (use these names in RFCs)

### 1) Faceted handles (least authority by construction)

Expose **different handles for different facets** of the same object:

- `read` vs `write`
- `inspect` vs `mutate`
- `request` vs `grant`

DeriveBSD implication: schemas and contracts should model these as **distinct capability types**, not flags.

### 2) Attenuating proxies (a.k.a. “attenuators”)

If you have capability `C`, you can create a proxy `C'` that forwards only a subset of operations.

Use for:
- “read-only” views
- rate limits
- method allowlists
- parameter bounds

DeriveBSD implication: capability routers and portals should support **proxy construction** as a first-class operation.

### 3) Revocation by indirection (the default revocation story)

Hard truth: if you hand out a raw unforgeable reference, you can’t always claw it back.
The standard solution is **one level of indirection**:

- You grant `C = (resolver, key)` rather than `C = (target)`.
- The `resolver` maps `key -> target` as long as the grant is live.
- Revocation = delete/disable the mapping.

DeriveBSD already uses this mental model in leases and name→capability indirection.
Make it explicit and uniform.

See also: capability directories (Amoeba lesson) and lease envelopes.

### 4) Leases (revocation + time as a primitive)

A lease is a capability whose validity is bounded by:

- **time** (expires automatically)
- **budget** (bytes/ops/timeouts)
- **state** (revoked if policy changes)

DeriveBSD implication: any capability that crosses a trust boundary should either:

- be a lease, or
- be reachable through revocable indirection.

### 5) Membranes (deep attenuation across trust boundaries)

A membrane wraps all references crossing a boundary so that:

- all calls can be mediated (logging/policy/budget)
- any newly obtained capabilities are also wrapped (deep attenuation)
- revocation can cut off the whole boundary at once

This is the “don’t let authority leak through return values” answer.

DeriveBSD implication:
- Portal sessions should behave like membranes.
- Any “capability router” that connects components should have an optional membrane mode.

## The checklist (required in feature intake)

When an RFC introduces a capability type or broker:

1) **Attenuation story**
   - Which pattern? (facet/proxy/membrane/lease)
   - What is the smallest safe default?

2) **Revocation story**
   - Indirection? Lease expiry? Both?
   - What does revocation look like in receipts/events?

3) **Blast-radius surface**
   - Where does a new method/authority show up in diffs?
   - What contract digest changes?

4) **Replay / auditability**
   - Can we reconstruct “who could do what, when” from evidence?

See: `docs/348-design-review-rubric-and-feature-intake.md`, `docs/252-lease-envelope-and-cross-lane-joins.md`.

## Where this plugs in

- Portals / powerbox: `docs/179-portals-and-powerbox.md`
- Object-capability RPC + contract digests: `docs/183-object-capability-rpc.md`
- Remote capability transport: `docs/353-captp-ocapn-remote-capabilities.md`
- Leases + revocation events: `spec/lease.snapshot.schema.json`, `spec/lease.revoke.event.schema.json`
- Name→capability indirection: `docs/345-amoeba-bullet-server-and-capability-directories.md`

## References

- Mark S. Miller et al., *Capability Myths Demolished* (membranes, attenuation, confinement):
  https://web.archive.org/web/20190107141354/http://www.erights.org/elib/capability/duals/myths.html
  (also circulated as a technical report / paper PDF in multiple venues)
- Joe Duffy, *Objects as Secure Capabilities* (Midori lessons, KeyKOS lineage):
  https://joeduffyblog.com/2015/11/10/objects-as-secure-capabilities/
- Object-capability model overview:
  https://en.wikipedia.org/wiki/Object-capability_model

Last updated: 2026-02-27r101
