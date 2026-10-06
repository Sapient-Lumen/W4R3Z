# ADR-0105: Stronger packet-capture raw-byte export must carry explicit approval evidence

Date: 2026-03-09  
Status: Accepted

## Context

`adrs/ADR-0104-packet-capture-export-proof-chain-and-profile-posture.md` already fixed the proof chain for stronger packet-capture raw-byte export.
A normalized packet artifact now stays on the generic `export.policy` / `export.receipt` lane and must join back to the bounded session, summary, safe-open import receipt, and redaction receipt.

That still leaves one operator-facing ambiguity:
**what proves that this stronger export was deliberately approved by a real actor instead of quietly flowing through a generic export path?**

Without a tighter answer, implementations can still drift into a bad compromise:

- the packet-capture export receipt shows a valid proof chain,
- but the export is effectively authorized by an ambient or automatic path,
- and the approval story is reconstructed later from logs or social process.

That is too weak for a stronger raw-byte export lane.
DeriveBSD already has the right generic approval substrate: `consent.request` and `consent.receipt`.
The next step should be a constrained packet-capture export profile over that lane rather than a new approval subsystem.

## Decision

**A stronger `packet.capture.normalized` export must carry explicit approval evidence on the generic consent lane, and that approval may not be `auto`.**

Specifically:

1. Keep approval on the generic consent substrate.
   - Do **not** add a packet-capture-only approval subsystem.
   - Reuse `consent.request` / `consent.receipt` and profile them narrowly for stronger packet-capture exports.

2. Require a typed approval request for stronger packet exports.
   - The canonical packet-capture export consent request profile must stay an `action.kind = export` request.
   - It must bind at least the governing `policy_digest`, exported `artifact_digest`, and `lease_id`.
   - It must require `secure_attention_required = true` so a stronger packet export is not treated like an ambient background upload.

3. Require real approval evidence for stronger packet exports.
   - The canonical packet-capture export consent receipt profile must remain a constrained `consent.receipt`.
   - It must represent an actual approval outcome and disallow `method = auto`.
   - GUI, TTY, and OOB approval remain valid so A–D do not fork.

4. Bind stronger packet exports back to that approval evidence.
   - `spec/packet.capture.export.receipt.profile.schema.json` must require `consent_receipt_digest` for `artifact.kind = packet.capture.normalized`.
   - Summary export remains the ordinary path and does not gain a packet-specific approval requirement.

5. Keep A–D coherent without freezing quorum counts.
   - This ADR does **not** decide exact quorum thresholds or approver rosters.
   - It only fixes that stronger packet raw-byte export cannot hide behind implicit or automatic approval.

## Consequences

- Stronger packet-capture raw-byte export now has a typed answer to both questions:
  - *why were these bytes exportable?* → the proof chain,
  - *who approved that stronger act?* → the consent evidence.
- Workstation UX can stay GUI/trusted-UI shaped, while fleet and factory lanes can stay TTY/OOB/quorum-capable.
- Implementations now have a narrow spec target for the approval edge of packet-capture export.

## What this does not decide

This ADR does **not** decide:

- exact quorum thresholds,
- exact approver groups,
- the transport or storage of OOB approvals,
- or whether transparency logging is mandatory for every stronger packet export.

Those remain generic export/posture questions.
This ADR only fixes the stronger export approval evidence boundary so `packet.capture.normalized` cannot be exported by “auto, but we logged it somewhere” folklore.
