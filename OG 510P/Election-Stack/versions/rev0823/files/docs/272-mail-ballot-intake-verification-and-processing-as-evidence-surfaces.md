# 272. Mail ballot intake, verification, and processing as evidence surfaces

**Track:** Shared  
**Status:** Draft (bounded; privacy-first; anti-weaponization)

This note defines a compact set of **publishable evidence surfaces** for the *back-office* workflow that turns returned vote-by-mail (VBM) / absentee ballot envelopes into tabulation-ready ballots, **without publishing voter PII** or operational details that enable targeting.

It composes with:
- Chain-of-custody patterns (`247`) and VBM logistics (`271`)
- Provisional/cure/canvass surfaces (`251`)
- Adjudication/duplication surfaces (`254`)
- ENR snapshot + corrections surfaces (`252`)
- CommitLog / transparency commitments (`261`)
- Canonicalization/signing/timestamping (`265`)

## Principles

1. **Aggregate, not individualized.** Publish counts, reason-code rollups, and hash commitments — not voter identifiers, signatures, envelope images, or ballot images.
2. **Append-only history.** Prefer “ledger + digest” (hash-chained rollups) over mutable spreadsheets.
3. **Two-person integrity & role separation.** Evidence surfaces should show that *roles exist and were used*, not who the people were.
4. **Stop conditions (hard).** Never publish information that:
   - reveals voter identities, signatures, addresses, or unique envelope/barcode identifiers
   - discloses facility layouts, camera placements, alarm details, or exploitable staffing patterns
   - enables harassment/intimidation or targeted disruption of collection/processing

## Minimal publishable artifact set

### A. Intake & custody (envelopes arrive)

**1) Intake Batch Digest (IBD)**  
A daily/shift digest that commits to:
- batch IDs (opaque; non-derivable), intake channel class (mail / drop-off / in-person handoff)
- counts received, counts quarantined/flagged, counts forwarded to verification
- custody handoff events summarized (counts + timestamps + role classes)

**2) Envelope Storage Posture Capsule (ESPC)**  
A short capsule stating:
- storage zones are controlled-access, monitored, sealed where applicable
- seal inventory summaries are maintained (see `266`)

### B. Eligibility / envelope verification (outer-envelope stage)

**3) Verification Policy Declaration (VPD)**  
A stable public declaration linking to authoritative jurisdiction policy sources (use `262`):
- what checks exist (e.g., signature review, ID/attestation requirements where applicable)
- what is *not* checked (to avoid misinformation)
- cure availability + deadlines (policy-level only; no case data)

**4) Verification Rollup Digest (VRD)**  
A periodic rollup:
- envelopes verified/accepted
- rejected/needs-cure counts by **reason code**
- re-reviewed/overturned counts (quality & consistency signal)
- “unknown/other” bounded and reviewed

**5) Rejection Reason-Code Dictionary (RRCD)**  
A tiny, change-controlled dictionary of reason codes used by VRD.  
Change-controlled via `256` (change control) and committed via `261` + `265`.

### C. Cure workflow (if applicable)

If curing exists, link to `251` and publish only:
- **Cure Policy Capsule (CPC)**: policy + channel options + deadlines (no voter lists)
- **Cure Outcomes Digest (COD)**: aggregate counts cured / not cured / pending by date window

### D. Opening / extraction / prep (inner-ballot stage)

**6) Opening Session Ledger (OSL)**  
Per-session rollups:
- start/end timestamps, number of workstations, role classes present (e.g., opener, observer liaison)
- envelopes opened, issues encountered (counts), ballots routed to duplication/adjudication (counts only)

**7) Separation Attestation (SA)**  
A short attestation that **identity-bearing materials** (outer envelope) are separated from ballots per local procedure, with custody controls.

### E. Scanning / tabulation feed (without results)

**8) Scanner Feed Digest (SFD)**  
Counts-only:
- ballots scanned, rejects/errors (counts by code), rescans (counts)
- cryptographic commitment to internal scan logs (hash-only, per `265`)

**9) Exceptions & Duplication Linkage**  
If duplication/adjudication occurs, publish only:
- counts routed + returned
- reference the aggregate surfaces in `254` (no per-ballot detail)

### F. Reconciliation bridges

**10) Processing → Canvass Bridge Digest (PCBD)**  
A simple bridge that ties:
- IBD + VRD + OSL + SFD totals  
to the canvass reconciliation ledger (`251`) and ENR corrections log (`252`).

## “Good transparency” defaults

- Publish a **daily digest** during peak processing windows, then a **final digest** at certification.
- Commit each digest to `CommitLog` (`261`) and optionally a public transparency log (`265`).
- Use clear public language: what is known, what is not known yet, and where the next verification point is.

## External anchors (cite-first)

- CISA/EI-GCC: **Signature Verification & Cure Process** (guidance + considerations).  
  xref: cisa_signature_verification_cure_process_final_508
- EAC: **Chain of Custody Best Practices**.  
  xref: eac_bestpractices_chain_of_custody_best_practices
- CISA: **Ballot Drop Box Resource Document** (collection/oversight considerations).  
  xref: cisa_ballot_drop_box_document
- NCSL: **How states verify voted absentee/mail ballots** (jurisdictional variation reminder).  
  xref: ncsl_14_how_states_verify_voted_absentee_mail_ballots
- NCSL: **When absentee/mail ballot processing and counting can begin** (recently updated; avoid assumptions).  
  xref: ncsl_ballot_processing_and_counting_can_begin_maptype_tile
