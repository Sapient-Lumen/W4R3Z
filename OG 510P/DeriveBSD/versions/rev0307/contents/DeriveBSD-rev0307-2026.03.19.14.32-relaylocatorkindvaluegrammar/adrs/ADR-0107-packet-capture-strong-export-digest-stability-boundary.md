# ADR-0107: Stronger packet-capture export proof chains must be digest-stable across normalization, approval, transport, and export

Date: 2026-03-09  
Status: Accepted

## Context

`adrs/ADR-0104-packet-capture-export-proof-chain-and-profile-posture.md` fixed the stronger packet-capture export proof chain.
`adrs/ADR-0105-packet-capture-strong-export-approval-evidence-boundary.md` fixed the approval edge.
`adrs/ADR-0106-packet-capture-strong-export-transport-boundary.md` then fixed the delivery edge by requiring transport evidence.

That still leaves one implementer-friendly escape hatch:
**the archive can prove that a stronger export was normalized, approved, and transported without proving strongly enough that all those receipts still refer to the same bytes.**

Without a tighter boundary, an implementation can drift into a weak compromise:

- approval is taken for one normalized derivative,
- transport evidence is emitted for another derivative or re-packed variant,
- export metadata points at a third digest,
- and reviewers are left reconstructing whether the stronger act stayed stable from redaction output to actual handoff.

The archive already has the right substrate for this boundary:

- `redaction.receipt` exposes the normalized output digest,
- `consent.request` exposes `action.artifact_digest`,
- `transport.receipt` exposes `artifact.digest`,
- `export.receipt` exposes `artifact.digest`,
- and `supporting_evidence` already binds the stronger act back to session / summary / import / redaction evidence.

The next step should therefore be a narrow rule over the existing fields rather than another packet-only object family.

## Decision

**A stronger `packet.capture.normalized` export proof chain must be digest-stable across normalization, approval, transport, and export.**

Specifically:

1. Reuse the existing receipt surfaces.
   - Do **not** add a packet-only proof-chain subsystem.
   - Keep the proof in the existing `redaction.receipt`, `consent.request`, `consent.receipt`, `transport.receipt`, and `export.receipt` lane.

2. Bind the stronger export to the normalized bytes.
   - For stronger packet export, the effective normalized artifact digest is the `output_digest` from the packet-capture `redaction.receipt`.
   - That digest is the anchor for the later approval / transport / export steps.

3. Require digest stability across the stronger action chain.
   - `consent.request.action.artifact_digest` must match the normalized output digest.
   - `transport.receipt.artifact.digest` must match the same digest.
   - `export.receipt.artifact.digest` must match the same digest.
   - The joined session / summary / import / redaction evidence must remain coherent with that digest.

4. Keep approval and transport evidence independently verifiable.
   - `consent.receipt.request_digest` should be verifiable against the actual consent-request object.
   - `export.receipt.consent_receipt_digest` and `export.receipt.transport_receipt_digest` should be verifiable against the actual joined receipts.

5. Treat example coherence as part of the contract.
   - The canonical packet-capture export examples should no longer use disconnected placeholder digests for the stronger path.
   - A lightweight checker should fail if the digest-bound chain drifts.

## Consequences

- Reviewers can now answer a stronger question than “was something approved and transported?”
  They can ask: **was this exact normalized artifact approved and transported?**
- Packet-capture stronger export stays explainable without new product-profile knobs.
- The archive becomes a better implementation target because the canonical examples now demonstrate a coherent proof chain instead of a bag of locally plausible placeholders.

## What this does not decide

This ADR does **not** decide:

- exact wire-level transport headers or adapter APIs,
- exact remote recipient storage semantics,
- exact transparency requirements for every profile,
- or whether all export lanes beyond packet capture should adopt the same checker immediately.

Those remain generic export/transport questions.
This ADR only fixes that the stronger packet-capture export chain must stay about the same bytes from normalization output to completed export.
