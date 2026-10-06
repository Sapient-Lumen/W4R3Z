# Breakglass supplementary accepted case-object proof stays validator-pinned when visible

**Tier:** B (Cross-cutting breakglass/export boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Bundles, Broker→Lease→Receipt, Adapter→Shadow→Replace

`docs/711` fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.
`docs/712` then fixed that supplementary breakglass adapter/runtime material stays receipt-first on typed redaction/export/transport proof when it travels.
`docs/713` then fixed that the same portable story still needs the exact `breakglass.receipt` digest.
`docs/714` then fixed that portable supplementary evidence stays artifactized and off live control locators.
`docs/715` then fixed that portable supplementary evidence must stay payload-anchored to at least one passive artifact digest or accepted case-object proof.
`docs/716` then fixed that accepted case-object proof must stay object-exact on the accepted remote attachment/object/message-part.

That still leaves one small but expensive seam:
**if the accepted-case-object lane is already object-exact, can it still float across mutable remote revisions when the adapter can see a stronger version / generation / ETag-like validator?**

## Accepted boundary

Keep accepted case-object proof **validator-pinned when visible**.

If richer supplementary breakglass adapter/runtime material travels portably and the payload anchor uses accepted case-object proof, keep the exact accepted remote attachment/object/message-part identity from `docs/716`.
Then, when the adapter can also see a stronger revision/version/generation/ETag-like validator for that exact accepted remote object, keep that validator pinned too.

The portable story should still read like:

- exact `breakglass.receipt` digests for typed emergency authority proof,
- typed `redaction.receipt` / `export.receipt` / `transport.receipt` handling proof,
- an object-exact accepted case-object proof when that lane stands in for payload identity,
- and the strongest visible remote validator for that exact accepted object when the adapter can actually see one.

## What this means in practice

### Object-exact is still the floor

This cut does not weaken `docs/716`.
The accepted-case-object lane still has to name the exact remote attachment/object/message-part.
A parent case/ticket/thread/container id is still context only.

### Mutable remote objects should not fall back to “latest object wins”

Some portals reuse the same accepted attachment/object id across revisions or expose an explicit version token alongside the accepted object.
If the adapter can see that stronger token, keep it.
Do not let an object-exact anchor silently drift back into “whichever revision of that object the portal shows now”.

### Keep the strongest visible validator, not a fake one

This rule is conditional on visibility.
If the adapter can see a strong `ETag`, attachment revision, generation token, or another opaque remote validator, preserve it.
If the adapter cannot see one, do not invent a pretend validator just to satisfy the archive.
In that case the `docs/716` object-exact floor still applies.

### This still stops short of the stronger packet-export stack

This cut does **not** require the whole stronger packet-export continuity stack for breakglass supplementary evidence.
It does not standardize remote protection posture, remote locator continuity, or metadata-only reverification here.
It only fixes the smaller next floor worth locking now:
accepted case-object proof should keep the strongest visible remote validator for that exact accepted object when the adapter can see one.

## Why this is the right narrow cut

The same identity lesson still applies.
RFC 9110 treats entity tags as validators for specific representations, and `If-Match` uses strong comparison to ensure state-changing requests apply to the expected current representation.
RFC 7232 explains that strong validators change when representation data observable in a 200 response changes.
And DeriveBSD already made the same practical move for stronger packet-capture export by insisting on remote-validator continuity (`docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`).

This breakglass cut deliberately stays smaller than that stronger lane, but it keeps the same basic discipline:
**if accepted case-object proof is going to stand in for payload identity and the adapter can see the remote revision/version token, keep it pinned instead of collapsing back to object-latest folklore.**

## First spec cut

The implementation cut is intentionally small:

- tighten `incident.bundle.includes.extra[]` and nearby bundle/breakglass docs so accepted case-object proof stays validator-pinned when the adapter can see a remote validator
- refresh the example bundle so the richer breakglass side-evidence trail shows an object-exact accepted-case-object proof placeholder that is also validator-pinned
- add a guardrail that fails if the archive stops saying visible validators on accepted external objects must stay pinned instead of being dropped

## What this does *not* decide

This cut does **not** decide:

- the future typed family for richer breakglass adapter-side evidence
- the exact typed schema for accepted case-object proof in that future family
- whether breakglass supplementary evidence should later require remote-protection / remote-locator continuity too
- or which support portals/case systems are approved to host accepted external case objects

It decides only the smaller boundary worth locking now:
**when accepted case-object proof is already object-exact and the adapter can see a stronger remote validator, keep that validator pinned too.**

## Related docs

- ADR: `adrs/ADR-0307-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md`
- accepted-case-object exactness floor: `docs/716-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md`
- packet-capture remote-validator inspiration: `docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`
- authority-first bundle contract: `docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md`
- receipt-first supplementary export boundary: `docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md`
- payload-anchor boundary: `docs/715-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support bundle contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- guardrail: `tools/check_breakglass_adapter_case_object_validator_boundary.py`

## References

- RFC 9110, *HTTP Semantics* (`ETag`, validators, and `If-Match` strong comparison): https://www.rfc-editor.org/rfc/rfc9110
- RFC 7232, *HTTP/1.1 Conditional Requests* (strong validators change with representation changes): https://www.rfc-editor.org/rfc/rfc7232

Last updated: 2026-03-23r448
