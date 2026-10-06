# Breakglass supplementary accepted case-object proof stays object-exact when portably carried

**Tier:** B (Cross-cutting breakglass/export boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Bundles, Broker→Lease→Receipt, Adapter→Shadow→Replace

`docs/711` fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.
`docs/712` then fixed that supplementary breakglass adapter/runtime material stays receipt-first on typed redaction/export/transport proof when it travels.
`docs/713` then fixed that the same portable story still needs the exact `breakglass.receipt` digest.
`docs/714` then fixed that portable supplementary evidence stays artifactized and off live control locators.
`docs/715` then fixed that portable supplementary evidence must stay payload-anchored to at least one passive artifact digest or accepted case-object proof.

That still leaves one small but expensive seam:
**if the payload anchor uses accepted case-object proof, can it stop at the parent case/ticket/thread id instead of naming the exact accepted remote object?**

## Accepted boundary

Keep accepted case-object proof **object-exact**.

If richer supplementary breakglass adapter/runtime material travels portably and the payload anchor uses accepted case-object proof, the archive-facing story should carry proof for the **exact accepted remote attachment/object/message-part identity**.
Parent case/ticket/thread/container ids may still travel as context, but they are not enough by themselves.

The portable story should still read like:

- exact `breakglass.receipt` digests for typed emergency authority proof,
- typed `redaction.receipt` / `export.receipt` / `transport.receipt` handling proof,
- and either a passive artifact digest or an **object-exact** accepted case-object proof for the payload that actually traveled.

## What this means in practice

### Parent case ids are context, not payload identity

A case number, incident thread id, or support portal container can still be useful.
But it does not answer the payload-identity question by itself.
If the payload anchor uses accepted case-object proof, keep the exact accepted remote attachment/object/message-part identity too.

### `extra[]` should not hide behind case-exact folklore

`incident.bundle.includes.extra[]` may still carry supplementary evidence digests.
When it carries richer supplementary breakglass adapter/runtime material and the payload anchor uses the accepted-case-object lane, do not let that proof collapse into only a parent case/ticket/container handle.
Keep the proof object-exact instead of case-exact.

That keeps the archive from saying only “something in CASE-8841 mattered here” when the real review question is “which exact accepted object was the payload anchor?”

### This stays smaller than the stronger packet-export stack

This cut does **not** require the whole stronger remote continuity stack for breakglass supplementary evidence.
It does not standardize `remote_validator`, `remote_protection`, or `remote_locator` continuity here.
It only fixes the smaller floor worth locking now:
accepted case-object proof must at least stay exact on the accepted remote object.

## Why this is the right narrow cut

The same evidence/identity lessons still apply.
NIST SP 800-86 describes collection as identifying, labeling, recording, and acquiring data while preserving integrity.
RFC 6920 formalizes naming the digital object itself with hash-based identifiers instead of relying on container folklore.
And DeriveBSD already made the same practical move in the stronger packet-capture lane by insisting on remote-object continuity (`docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`).

This breakglass cut deliberately stops earlier than that stronger lane, but it keeps the same basic discipline:
**if accepted case-object proof is going to stand in for payload identity, it should at least name the exact accepted object rather than only the parent case.**

## First spec cut

The implementation cut is intentionally small:

- tighten `incident.bundle.includes.extra[]` and nearby bundle/breakglass docs so accepted case-object proof stays object-exact rather than case-exact
- refresh the example bundle so the richer breakglass side-evidence trail can show an object-exact accepted-case-object proof alongside the passive artifact digest / handling receipts
- add a guardrail that fails if the archive stops saying accepted case-object proof must name the exact remote object rather than the parent case/ticket/container

## What this does *not* decide

This cut does **not** decide:

- the future typed family for richer breakglass adapter-side evidence
- the exact typed schema for accepted case-object proof in that future family
- whether breakglass supplementary evidence should later require remote-validator / protection / locator continuity too
- or which support portals/case systems are approved to host accepted external case objects

It decides only the smaller boundary worth locking now:
**accepted case-object proof may satisfy the payload-anchor rule only when it stays object-exact, not merely case-exact.**

## Related docs

- ADR: `adrs/ADR-0306-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md`
- authority-first bundle contract: `docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md`
- receipt-first supplementary export boundary: `docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md`
- authority-anchored supplementary handoff: `docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md`
- live-locator firewall: `docs/714-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md`
- payload-anchor boundary: `docs/715-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support bundle contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- packet-capture remote-object continuity inspiration: `docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`
- guardrail: `tools/check_breakglass_adapter_case_object_exactness_boundary.py`

## References

- NIST SP 800-86, *Guide to Integrating Forensic Techniques into Incident Response* (collection / identity / chain-of-custody guidance): https://csrc.nist.gov/pubs/sp/800/86/final
- RFC 6920, *Naming Things with Hashes* (object identity by hash rather than container folklore): https://www.rfc-editor.org/rfc/rfc6920.html

Last updated: 2026-03-23r447
