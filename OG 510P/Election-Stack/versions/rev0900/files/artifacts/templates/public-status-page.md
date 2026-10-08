# Public status page template (election day)

**Track:** Shared (cross-cutting)

This is a **digest-first view** over `PublicNotice` objects.
For a jurisdiction-grade pattern, see `DOC:docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`.

Invariants (Claude coherence):
- Every non-trivial claim on this page MUST be backed by a signed `PublicNotice` (or feed) and show its **digest short form** (copy/pasteable).
- Do not hedge (“likely / appears / seems / probably”) as a substitute for epistemic tags (`DOC:docs/218-epistemic-status-tags-and-confidence-rubric.md`).
- Keep it **MAPT-passable**: plain text, copyable digests, explicit `next_update_at` commitments, and no “PDF scan compliance” (`DOC:docs/187-publication-compliance-and-coverage.md`).


## Current status
- Last updated (UTC):
- Voting open: ✅ / ❌
- Bulletin board reachable: ✅ / ❌
- Witness quorum checkpointing: ✅ / ❌
- Known incidents: none / link

## Canonical pointers
- Latest `PublicNoticeFeed` digest (window):
- Latest PublicNotice signing-keyset digest:
- Mirrors (at least 2):

## Latest checkpoint
- Checkpoint ID:
- Tree size:
- Timestamp:
- Witness signers:
- Hash (copyable):

## If you have a receipt
- If your receipt is **PENDING** for more than Δ minutes, follow these steps:
  1) retry via alternate ingress
  2) export your intake receipt evidence
  3) contact hotline / local office
  4) consider supervised override / paper fallback (if available)

## Transparency
- Evidence bundle mirrors: list
- Verifier tools: list

## How to verify (one paragraph)
- Compare digests across mirrors/channels; if they differ, treat it as an incident and cite a parity snapshot digest (`DOC:docs/201-public-surface-parity-snapshots.md`).
