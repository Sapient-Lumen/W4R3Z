# ADR-0104: Stronger packet-capture raw-byte export must stay proof-bound and summary-first by profile

Date: 2026-03-09  
Status: Accepted

## Context

`adrs/ADR-0097-packet-capture-session-and-summary-first-export-boundary.md` already made packet capture summary-first.
`adrs/ADR-0101-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md` and `adrs/ADR-0102-packet-capture-normalization-redaction-receipt-boundary.md` then fixed the safe-open + normalization path for stronger packet artifacts.
`adrs/ADR-0103-packet-capture-evidence-joins-in-incident-bundles.md` kept support bundles on typed digest joins instead of default raw `.pcapng` members.

That still leaves one practical export hole:
**when normalized raw packet bytes do leave the system, what makes that act explainable enough to keep the summary-first boundary real across A–D?**

Without a tighter answer, teams can still drift into a bad compromise:

- packet-capture summary is declared the normal review surface,
- support bundles stay digest-first,
- but the actual external handoff quietly becomes “upload the normalized `.pcapng`”,
- and the export receipt says only that some bytes left under some policy.

That loses the proof chain that explains *why* this stronger export was acceptable:
which bounded session it came from, which summary object describes it, which safe-open import receipt admitted it, and which deterministic redaction receipt proved it ended at `packet-records-only`.

DeriveBSD already has the right general lane for exports: `export.policy` + `export.receipt`.
The next step should be a narrow profile over that lane rather than a packet-capture-only side channel or a new product-profile key.

## Decision

**Strong packet-capture raw-byte exports stay on the generic export lane, but they must be proof-bound by a typed packet-capture export profile and remain a stronger action than summary export across all profiles.**

Specifically:

1. Keep packet-capture export profile-shaped, not key-shaped.
   - Do **not** add a new `product.profiles` default key.
   - Treat packet-capture export posture as a compiled consequence of the already-decided `evidence`, `evidence_exports`, and packet-capture boundaries.

2. Keep `packet.capture.summary` as the ordinary export class.
   - The canonical packet-capture export policy profile must include a `packet.capture.summary` rule with `allow_raw_blobs = false`.

3. Treat normalized raw-byte export as a stronger explicit class.
   - If policy allows a normalized raw packet artifact to leave the system, it uses a distinct `packet.capture.normalized` rule on the generic `export.policy` lane.
   - That rule remains explicit and still requires deterministic redaction evidence.

4. Bind stronger raw-byte exports to typed supporting evidence.
   - `export.receipt` gains an optional `supporting_evidence[]` join surface for typed proof-chain refs.
   - The canonical packet-capture export receipt profile must require:
     - the exported artifact class (`packet.capture.summary` or `packet.capture.normalized`),
     - and for `packet.capture.normalized`, supporting evidence roles for the session, summary, import receipt, and redaction receipt.

5. Keep A–D coherent without forks.
   - Across all profiles, summary export remains the ordinary path.
   - Normalized raw-byte export remains stronger and inherits each profile’s already-decided export posture (trusted-UI-visible on B, stronger approval/transparency posture on D, brokered/explicit posture on A/C).

## Consequences

- Export receipts can now explain why a stronger normalized packet artifact was exportable instead of only recording that bytes left the system.
- Summary-first remains true even when a normalized `.pcapng` is exceptionally exported.
- A/B/C/D keep one export lane and one profile vocabulary instead of growing a packet-specific product knob.
- Implementations now have a narrow typed policy/receipt shape for stronger packet-capture exports.

## What this does not decide

This ADR does **not** decide:

- the exact approval threshold mapping from `evidence_exports` posture to packet-capture raw-byte exports in each deployment,
- the transport backend or ticketing system,
- or whether every normalized derivative is exportable in every environment.

It only fixes the proof-bound export shape so the already-decided packet-capture lane does not collapse back into “ship the `.pcapng`” folklore.
