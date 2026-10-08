# 180 — Receipts & Gossip Attachments (Anti–Selective Disclosure)

**Track:** Shared

## Why this exists
Attackers often win by corrupting the **verification ecosystem** rather than the tally: selective disclosure, split views, and "only friendly challenges".

This doc standardizes a small set of **attachment relations** that make bad news hard to hide:

- a **transparency receipt** that proves an item was submitted / included (or at least acknowledged) by a log,
- a **gossip summary** that disseminates digests of what was (and was not) seen across perspectives.

These attachments are **integrity-bound** because `attachments` are included in the `tbs_digest` signing input (see `docs/176`).

## Attachment pointers
Attachments are represented as `EvidencePointer` objects (see `schemas/EvidencePointer.json`).

Preferred field names:
- `media_type` (MIME type)
- `rel` (relation label)

Backward-compatible alias:
- `content_type` is accepted but **deprecated**.

## Reserved rel values
These are the reserved relation labels for `EvidencePointer.rel`:

- `transparency_receipt` — points to a JSON object matching `schemas/TransparencyReceipt.json`.
- `gossip_summary` — points to a JSON object matching `schemas/GossipSummary.json`.
- `consistency_proof` — optional; profile-defined proof that binds log history across time.
- `inclusion_proof` — optional; profile-defined inclusion proof for a specific entry.

Notes:
- Receipts may be COSE-based (common in SCITT ecosystems) or other profile-defined formats; this archive uses a **generic receipt schema** so Track A can ship without locking to a single draft.

## When attachments are REQUIRED
Attachment requirements are declared in:

- `artifacts/registries/envelope-attachment-requirements.csv`

Verifiers and CI MUST treat that registry as authoritative.

Default policy (current):

- Any envelope kind whose publication could be selectively disclosed MUST carry:
  - `transparency_receipt`
  - `gossip_summary`

This typically includes:
- ENR updates
- inspection suppression reports
- governance updates (North Star)

Coverage reports MAY include receipts and SHOULD be gossiped.

## Practical verifier behavior
Offline verifier expectations:

1. Verify the primary envelope (`payload_digest`, `tbs_digest`).
2. Resolve each attachment pointer to bytes and verify the sha256 digest.
3. If `transparency_receipt` is required but missing → mark evidence as **incomplete** and emit a missing-attachment finding.
4. If `gossip_summary` is required but missing → mark as **selective-disclosure risk**.

## Why gossip summaries exist
Receipts prove *inclusion*, but they do not ensure everyone sees the same world.
Gossip summaries let multiple observers compare what they saw and produce **suppression evidence** when worlds diverge.

This mirrors the motivation behind transparency log gossip in the broader ecosystem.
