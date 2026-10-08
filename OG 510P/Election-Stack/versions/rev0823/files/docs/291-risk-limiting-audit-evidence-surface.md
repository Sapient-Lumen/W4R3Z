# 291. Risk-limiting audit evidence surface (digest-first)

**Track:** Shared / Verification

This document treats a Risk-Limiting Audit (RLA) as an **evidence surface**: a bounded set of *publicly auditable claims* supported by **digests, receipts, and controlled disclosure**, not raw ballot images, CVRs, or full workpapers.

It composes with:
- Digest-first kit: `docs/281`
- Controlled disclosure packet: `docs/282`
- Triage tags: `docs/283`
- Transparency anchoring: `docs/284`
- Signed digest statements (SDS): `docs/285`
- Key management/rotation: `docs/286`
- Timestamp receipts (TSR): `docs/287`
- External verification protocol: `docs/289`
- Public incident bulletin: `docs/290`

## Why this exists (bounded)
RLAs provide statistical assurance for reported outcomes by checking a random sample of the voter-verifiable audit trail (typically paper ballots). They are widely described as a “gold standard” post-election tabulation audit. (xref: `nist_gentle_intro_rla_pdf`, `eac_post_election_tabulation_audit_guide_2024_pdf`, `asa_post_election_audit_best_practices_2018_pdf`)

This archive’s focus is **operational evidence**: how to publish verifiable *summaries* of what was done, with receipts, while minimizing exposure of sensitive data and avoiding “dump the logs/ballots”.

## RLA evidence surface: minimal claim-set
A jurisdiction can publish a bounded, digest-first set of claims:

1. **RLA parameters** (risk limit, contests audited, method, stopping rules, sampling unit, escalation triggers).
2. **Chain-of-custody window** for the audit trail used (what physical artifacts were eligible).
3. **Randomness & selection** (how randomness was generated/verified; how the sample was derived).
4. **Sample manifest** (what was selected; where it was found; replacements if any).
5. **Human interpretation protocol** (how auditors adjudicated voter marks; dispute handling).
6. **Discrepancies** (categorized; magnitude; whether they increase sample size).
7. **Stopping condition** (why the audit stopped or escalated; whether a full recount was required).
8. **Outcome statement** (whether the reported outcome is confirmed within the chosen risk limit).

Each claim is supported by **digests** of the underlying artifacts and (optionally) **receipts** (SDS/TSR/transparency anchors).

## Canonical digest artifacts (publishable by default)
Create these as **digest artifacts** (do not publish raw ballots/workpapers by default):

- **RLA Plan Digest (RPD):** parameters + procedures + responsible roles.
- **Seed/Randomness Digest (SRD):** randomness source description + commitments + verification notes.
- **Sample Manifest Digest (SMD):** selected items, lookup process, replacements, exception log.
- **Interpretation Log Digest (ILD):** *counts* and *categories*, not ballot images.
- **Discrepancy Digest (DD):** discrepancy types, totals, escalation decisions.
- **RLA Outcome Certificate Digest (OCD):** the final outcome claim-set above.

Recommended: represent each of these as a **Signed Digest Statement** (SDS) and attach **Timestamp Receipts** (TSR) and/or transparency anchors for time & non-equivocation (`docs/284–287`).

## Template: RLA evidence summary (HFV)
Use `artifacts/templates/hfv.rla_evidence_summary.v1.json` to serialize the publishable summary for this surface.

Minimum interoperability expectations:
- All digests are **sha256** of canonical bytes (or sha256 of a canonical bundle) with an explicit `digest_scope`.
- Each digest object carries `triage` (optional) and `controlled_disclosure` pointer where raw material exists (`docs/282–283`).
- Optional `transparency_log` block if anchored (`docs/284`).

## Threat model notes (tight)
This surface is meant to reduce:
- **Ambiguity attacks:** unclear parameters or selection method after the fact.
- **Selective disclosure:** revealing only favorable fragments without a signed, timestamped envelope.
- **Privacy leakage:** accidental release of ballot-level data or voter-identifying chain-of-custody details.

This surface does **not** by itself fix:
- No trustworthy audit trail (e.g., no paper record suitable for audit).
- Broken custody/handling of audit materials (requires separate controls).

## External verification
A third party can verify:
- The published claim-set is internally consistent.
- Digests match disclosed packets (when disclosed).
- Receipts/anchors/timestamps prove “existence by time” and reduce equivocation.

Use `docs/289` and keep disclosures bounded (`docs/282`).

## Sources (pinned IDs)
- NIST: “A Gentle Introduction to Risk-Limiting Audits” (xref: `nist_gentle_intro_rla_pdf`)
- EAC: “Post-Election Tabulation Audit Guide” (xref: `eac_post_election_tabulation_audit_guide_2024_pdf`)
- American Statistical Association: “Principles and Best Practices for Post-Election Tabulation Audits” (xref: `asa_post_election_audit_best_practices_2018_pdf`)
- Colorado RLA overview/FAQ (xref: `co_sos_rla_faq_page`)
