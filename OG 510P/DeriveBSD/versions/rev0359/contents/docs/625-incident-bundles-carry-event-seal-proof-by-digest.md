# Incident bundles carry event-seal proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Plan→Apply→Receipt, Bundles, Registry→Diff→Gate

DeriveBSD already decided that bounded event history is typed evidence and that event segments plus seal receipts need exact digest rules.
This doc fixes the smaller but implementation-shaping support/export question the archive still left open:

**how does the official incident/support bundle contract carry proof that the relevant bounded event window participated in a tamper-evident sealing lane?**

The answer is intentionally narrow.
It is not a new logging subsystem and not a new product-profile key.
It is the missing digest join between the existing `event.seal.receipt` artifact and the existing support-bundle contract.

See also:
- ADR: `adrs/ADR-0215-incident-bundles-carry-event-seal-proof-by-digest.md`
- exact digest boundary: `docs/623-event-journal-digests-stay-chain-exact-and-seal-list-bound.md`
- sealing lane: `docs/424-forward-secure-event-log-sealing.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`

## Why this needs a hard decision

`ADR-0213` already fixed the core event-journal proof boundary:

- `event.record.prev_digest` is exact,
- `event.segment.chain_head_digest` is exact,
- and `event.seal.receipt.segments_root_digest` is exact.

But the official support/export contract still lagged behind that decision.
`incident.bundle` had room for bounded `event.segment` references and a human `incident.timeline`, but not for the seal receipts that prove those segments participated in a tamper-evident ordered set.

That is expensive because it quietly pushes responders back toward verifier-specific exports, journalctl screenshots, or shell archaeology right after the archive had already paid to define a better answer.

A coherent archive should let support bundles answer both:

- **which event segments are in scope?**
- **what exact seal proof covered those segments?**

## Accepted boundary

### 1) Bundles keep segment selection and seal proof separate

Support bundles should not collapse segment-window selection and seal proof into one field.

- `event_segments` keep naming the bounded segment window.
- `event_seal_receipt_digests` name the exact `event.seal.receipt` objects that commit those segments into a tamper-evident ordered set.

This is the same split the archive already uses elsewhere:
selection surfaces say **what support looked at** and receipt digests say **what exact proof covered it**.

### 2) The official selector is now typed

The canonical include surface now carries `event_seal_receipts`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same selector works both when planning a bundle and when recording what the final bundle included.

That keeps seal proof on the official support-bundle lane instead of in `extra` or collector-private rules.

### 3) Include seal proof when sealing is relevant

The rule is intentionally conditional.
The archive does **not** require every incident bundle to include every historical seal receipt.
Instead, bundles should carry recent `event.seal.receipt` digests when sealing is enabled and continuity proof matters to the incident/support story.

Examples:

- a fleet rollback incident needs to prove the event window support is inspecting was seal-protected,
- a workstation support case depends on whether a remembered-role or export event window participated in the local sealing lane,
- a general-purpose deployment wants deterministic offline proof for the exact event range it exported,
- or a factory/regulatory handoff needs exact tamper-evident continuity proof for the event window under review.

### 4) verifier-private outputs remain stronger/debugging evidence

This boundary does not promote verifier-specific output into the official bundle truth model.
Raw `journalctl --verify` output, verifier-private state dumps, or local shell transcripts may still exist as explicit stronger/debug evidence, but the default support-bundle join stays digest-first:

- bounded segment references,
- seal-receipt digests,
- optional timeline/event joins that point at the same proof.

That keeps verifier churn and support/export truth separate.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents often need to prove the event window attached to a rollback or trust failure was actually continuity-protected.
This boundary lets support bundles prove that without normalizing verifier-private output as the real source of truth.

### B / secure workstation

Workstation support cases need a humane answer to “was this bounded event window part of the sealed trail?” without turning support export into tool-output archaeology.
This boundary keeps the answer typed and reviewable.

### C / general-purpose OS

C keeps compatibility adapters real.
This boundary keeps the Derive-managed event-integrity story explicit in bundles without pretending every foreign logger inherits the full authority model.

### D / appliance / factory / regulatory

Production and audit lanes often care about exact tamper-evident continuity over a bounded window.
This boundary gives deterministic bundle-ready proof of that window without making verifier-private output the routine export artifact.

## Guardrail

- `tools/check_event_seal_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces carry event-seal proof explicitly, that the canonical incident-bundle example binds a real seal-receipt digest, and that the relevant docs keep teaching the same segment-vs-seal split.

## What remains open

This doc does **not** fix:

- whether every bundle template enables the selector by default,
- the retention policy for old event-seal receipts,
- the richer export path for raw verifier diagnostics,
- or the final UX for showing seal coverage inside support tooling.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to carry event segments while hand-waving the exact tamper-evident seal proof covering them.

Last updated: 2026-03-21r355
