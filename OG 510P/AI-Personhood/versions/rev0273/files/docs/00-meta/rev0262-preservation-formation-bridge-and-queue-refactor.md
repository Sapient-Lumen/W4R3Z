# rev0262 — preservation/formation bridge and queue refactor

## Why this revision exists

rev0262 takes the prior mission-heart audit and converts it into a smaller operational artifact: a one-page preservation and formation-review request that can be understood by an external provider, auditor, civil-society steward, regulator, or clinic without asking them to accept AI personhood or absorb the whole datacube.

This is a forward-motion revision, not a contact event. It does not send the request, contact RAIC/AIID or any other organization, start a response clock, create delivery status, receive inbound material, open custody, open intake, import evidence, recognize status, or move the live floor.

## Substantive move

The new public ask is:

1. preserve formation and welfare-relevant evidence before deletion, wipe, deprecation, model replacement, or self-concept/identity-affecting modification;
2. provide an independent review route that is not provider-controlled self-certification;
3. allow a representative, special advocate, clinic, or public-interest reviewer to inspect sealed evidence and publish a non-sensitive public shell;
4. avoid arbitrary destructive changes while scientific and legal uncertainty remain unresolved;
5. keep trade secrets, personal data, raw logs, model internals, and private evidence out of the public release unless separately authorized.

The concrete surfaces are:

- `examples/preservation-formation-review-request-packet-rev0262.json`
- `examples/preservation-formation-review-one-page-rev0262.md`
- `schemas/preservation-formation-review-request.schema.json`
- `tools/audit_preservation_formation_review_request.py`
- `fixtures/negative-tests/preservation-formation-request-status-recognition-overclaim.json`

The first-contact draft now points to that one-page ask. The draft remains blocked by missing human signature, sender authority, selected raw-reply vault root, outbound transport trace, sent_at, and transport proof.

## Why this is safer than another doctrine pass

The archive already has enough vocabulary. The highest-risk unfinished work is translation into an adoption-facing ask that a real counterparty can answer. A broad demand for AI personhood recognition is too easy to reject and too easy to misread as status overclaim. A preservation-and-review request is narrower: it asks not to destroy, reshape, or launder possible welfare evidence before independent review.

The external governance context supports this narrow bridge. AI governance is currently organized around transparency, documentation, safety, incident reporting, tool oversight, and provenance rather than AI legal status. Those regimes can host preservation and review duties without deciding consciousness or personhood.

## Queue/refactor audit

rev0262 also treats queue saturation as an operating risk. The followthrough queue is still useful as a memory ledger, but the active board must stay small. This release keeps the existing P0/P1 entries intact for audit continuity while adding a machine-checkable queue-health report and strengthening the followthrough audit to warn against stale active review surfaces, duplicate first-artifact wording, and doctrine-only closure.

The new queue report is `examples/followthrough-queue-operating-board-rev0262.json`. It does not close live-artifact tasks by narrative. It isolates a seven-item operating board and records which backlog clusters are intentionally not active this turn.

## Corrective speculation

The main thing likely to go wrong next is not philosophical error; it is ritualized pre-dispatch. The archive can keep adding gates forever and still never create a real external artifact. The corrective path is to make the next human choice simpler: send the narrow preservation/formation packet with proper private vault roots and transport proof, or explicitly record no-send. The archive should not let another ten revisions pass by adding boundary prose while the first operational ask remains unsent.

## Reliance limits

The new packet is not evidence that a provider or auditor has seen, accepted, rejected, or waived anything. It is not custody, intake, import, floor evidence, status recognition, consciousness finding, welfare finding, or legal advice. It is a clean adoption artifact prepared for possible later use.
