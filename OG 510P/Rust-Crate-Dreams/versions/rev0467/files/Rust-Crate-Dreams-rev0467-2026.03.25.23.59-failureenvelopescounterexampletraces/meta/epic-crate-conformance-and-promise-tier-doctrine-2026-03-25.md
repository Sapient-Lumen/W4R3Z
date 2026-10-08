# Epic crate conformance and promise-tier doctrine — 2026-03-25

This note answers a practical question the archive had not made explicit enough:

**What exactly should a worthy crate say when it claims support, compatibility, readiness, or trustworthiness?**

## Main judgment

A worthy crate should usually **not** emit one binary badge like “supported”.
It should emit a **tiered claim with basis**.

## Default claim vocabulary

Use a bounded tier ladder like this unless a lane has a better domain-specific version:

1. **unknown** — no claim yet
2. **declared** — maintainer declaration only
3. **built** — built or hosted successfully on named surface
4. **replayed** — locally rerun under a reproducible recipe
5. **exercised** — tests / witness programs / probes ran on a named matrix
6. **observed** — field or downstream integration evidence imported
7. **qualified** — extra assurance artifacts or domain-specific process evidence supplied
8. **refused** — lane intentionally declines to make a claim

A claim should also name its **dimension**:
- docs,
- target,
- toolchain,
- debugger,
- public API / boundary,
- source parity,
- supply-chain continuity,
- compile/build feedback,
- or another explicit surface.

## Claim basis doctrine

Never ship a claim without basis fields.
Minimum basis:
- claim dimension,
- tier,
- operator or generator,
- substrate used,
- matrix/profile scope,
- last-checked time,
- and refusal / unknown reason when applicable.

## Default conformance artifact family

A strong first conformance kit usually includes:

### A. `claim-envelope.json`
This is the compact reviewed claim.
It should summarize:
- dimension,
- tier,
- matrix or profile,
- basis pointers,
- and refusal / expiry / rerun metadata.

### B. `probe-record.jsonl`
This is the append-only raw observation stream.
It should contain:
- local probe outcomes,
- hosted import events,
- cargo/doc/debugger run receipts,
- and degraded / failed attempts.

### C. `conformance-summary.md`
This is the human-facing support sheet.
It should explain:
- what is claimed,
- what is merely declared,
- what was actually replayed or exercised,
- and what is outside scope.

### D. `claim-diff.json`
This is the machine-readable change surface.
It should say:
- which dimensions changed,
- which tiers changed,
- whether the basis changed,
- and whether human review is required.

### E. `recheck-plan.json`
This is the operating loop.
It should name:
- triggers,
- cadence,
- required environments,
- downgrade / expiry rules,
- and supersession policy.

## Release doctrine

### Honest `0.1`
Ship:
- one clear dimension or small dimension family,
- one bounded tier vocabulary,
- one stable claim envelope schema,
- one short human summary,
- one raw receipt stream,
- and explicit unknown/refused states.

Do **not** ship at `0.1`:
- fake universality,
- blanket “production-ready” language,
- giant policy taxonomies,
- or domain qualification claims you cannot defend.

### Strong `0.3`
Add:
- multiple profiles,
- imported hosted evidence,
- richer diffing,
- stronger corpora,
- and reusable policy/profile presets.

### Real `1.0`
Usually means:
- tier meanings are stable,
- packet schema evolution policy is explicit,
- recheck semantics are stable,
- and human handoff semantics match machine packets.

## Anti-patterns

### Anti-pattern 1 — binary support badge
Symptoms:
- “supported” with no target list,
- no distinction between declared and replayed,
- no date or generator,
- no refusal state.

### Anti-pattern 2 — raw data masquerading as a claim
Symptoms:
- many probe logs,
- but no stable envelope for reviewers,
- no downgrade rules,
- no support summary.

### Anti-pattern 3 — qualification theater
Symptoms:
- safety / security / enterprise wording,
- but no extra artifacts, no domain profile, no process basis.

### Anti-pattern 4 — unstable substrate baked into stable meaning
Symptoms:
- docs.rs defaults or Cargo internals directly redefine the packet schema whenever they move.

## Practical archive rule after this pass

When planning a top-lane crate, the archive should now answer:
1. which support dimensions it claims,
2. which tier vocabulary it uses,
3. which artifacts are raw versus reviewed,
4. when the claim must be rerun,
5. and what the crate explicitly refuses to certify.

If the pass cannot answer those questions, the lane is still underplanned.
