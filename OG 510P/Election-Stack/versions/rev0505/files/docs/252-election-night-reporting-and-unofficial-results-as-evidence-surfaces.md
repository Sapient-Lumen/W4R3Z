# 252 — Election night reporting and unofficial results as evidence surfaces (ENR, corrections, and non-finality)

**Track:** Shared

This document defines a **minimal, publishable evidence surface** for **Election Night Reporting (ENR)** and other **unofficial results reporting**.
It aims to increase *checkability* (the public can verify that you behaved consistently) without pretending that unofficial results are “final,” and without publishing sensitive details that enable interference.

External anchors (reference only):
- EAC: Election Night Reporting (ENR) systems overview: xref: eac_technology_estep_program_night_report_systems
- EAC: *Quick Start Guide: Election Results Reporting*: xref: eac_quickstartguides_results_reporting_eac_quick_start_guide_508
- EAC: *Checklist for Securing Election Night Results Reporting*: xref: eac_enr_securing_results_checklist_pdf
- CISA: *Election Results Reporting: Risks and Mitigations*: xref: cisa_results_reporting_risk_mitigations_508
- NIST: Election Results Reporting Common Data Format (CDF): xref: pages_nist_gov_electionresultsreporting

## Scope

Covers:
- The **unofficial results** reporting pipeline (collection → aggregation → publication → corrections).
- **Public comms artifacts** that explain “why totals change” and what *100% precincts reporting* does and does not mean.
- A minimal **corrections + provenance** model suitable for publishing and third‑party comparison.

Does **not** cover:
- How to attack ENR or voting systems.
- State‑specific legal rules (this is a general template, not legal advice).
- Tabulation integrity (covered elsewhere); ENR is *reporting*, not *counting*.

## Core claims we want to be able to support

Your ENR posture should allow a verifier to reasonably conclude:

1. **Non‑finality is explicit.** Unofficial results are labeled and explained as non‑final at every public surface.
2. **Publication is consistent.** Updates follow a stable cadence/trigger, and changes are explainable.
3. **Corrections are accountable.** Every correction has a timestamp, scope, reason-code, and provenance reference.
4. **Separation is credible.** Reporting systems are separated from tabulation and are designed/operated to reduce interference risk.
5. **Aggregation is reproducible.** A third party can re-aggregate published precinct/contest totals (where published) and match the headline numbers, or see exactly why it cannot.

## Minimal publishable artifacts

### A. ENR “Non-Finality Banner” (required)

A short, stable text block placed on:
- ENR website/app
- social posts that include totals
- press releases / situation updates

Minimum content:
- “Unofficial results; not certified”
- “Totals may change during canvass due to late-arriving eligible ballots, provisional ballots, adjudication, and reconciliation”
- link to your **Post‑Election Process explainer** (your own page or `docs/251-*`-style explanation adapted to jurisdiction)

### B. ENR System Statement (publishable architecture posture)

A 1–2 page statement (or web page) that includes:
- ENR purpose: “reporting unofficial totals”
- data inputs (what files, from where, by whom, and when)
- separation posture (e.g., *reporting system is not used for tabulation*)
- who has access and what change controls exist
- publication channels (web, API, socials, mirrors)

Avoid:
- IP addresses, vendor credentials, exact firewall rules, or other operational secrets.

### C. Unofficial Results Snapshot Pack (URSP)

At each public update (or at least each major update), publish or internally generate:

- `results-unofficial-YYYYMMDD-HHMM.json` (or CSV) using a stable schema
- `results-unofficial-YYYYMMDD-HHMM.sha256`
- `results-unofficial-YYYYMMDD-HHMM.meta.json` containing:
  - `generated_at`
  - `source_batch_id` (human meaningful)
  - `coverage` (what precincts/ballots are included)
  - `notes` (free text)
  - `errata_ref` (pointer to corrections log entry if applicable)

If you can publish only *some* of these publicly, you can still publish:
- the hash file, metadata, and a redacted/aggregated results file
- plus a statement describing what is withheld and why (privacy, safety, law)

### D. Corrections log (public, append-only)

A small table (or JSONL) with entries:

- `id` (monotonic)
- `timestamp`
- `scope` (jurisdiction / contest / precinct group)
- `reason_code` (see below)
- `delta_summary` (e.g., “+312 votes added to Contest X from Batch Y”)
- `references` (link to URSP snapshot ids and any public notices)

Suggested reason codes (keep compact):
- `LATE_ELIGIBLE_BALLOTS`
- `PROVISIONAL_RESOLUTION`
- `ADJUDICATION_UPDATE`
- `RECONCILIATION_FIX`
- `DUPLICATE_REMOVAL`
- `DATA_PIPELINE_FIX`
- `REPORTING_DISPLAY_FIX`
- `OTHER_EXPLAINED`

### E. “Why totals change” explainer (short)

A short explainer page (ideally evergreen) that answers:
- what ENR is and is not
- why totals change
- what “100% precincts reporting” means on your system
- when certification happens and where official results live

The EAC quick-start guide and checklist are good anchor references for this style of guidance.

## Tight linkage to existing archive concepts

- **EvidenceEnvelope / signed releases:** align URSP with `adr/0004-*` + `docs/238-results-release-packages-as-evidence-envelopes.md` + `docs/236-results-release-transparency-profile.md`.
- **Canvass reconciliation:** link the corrections log to the reconciliation narratives in `docs/251-provisional-ballots-curing-and-canvass-as-evidence-surfaces.md`.
- **Ops comms:** ENR banners + update cadence should follow `docs/247-ops-security-controls-comms-and-chain-of-custody.md`.

## Publishable-proof matrix (minimal)

| Control | What you can publish safely | What you should *not* publish |
|---|---|---|
| Non-finality clarity | banner text + explainer URL + timestamps | internal comms, drafts with sensitive incident detail |
| Snapshot integrity | hashes + signed snapshot ids + metadata | internal network topology / access paths |
| Correction accountability | append-only log + reason codes + linked snapshots | voter-identifying information, ballot images |
| Separation posture | “ENR is reporting only” statement + high-level data flow | step-by-step operational security procedures |
| Reproducibility | precinct/contest totals (where lawful) + schema | anything that increases attack surface unnecessarily |

## Stop conditions (anti-weaponization)

If a proposed “transparency improvement” would:
- expose operational security details,
- enable targeted harassment (naming staff/volunteers),
- expose voter PII or ballot secrecy risk,
- create incentives for malicious “challenge spam,”

…then **do not publish it**. Use *hashes, high-level descriptions, and controlled disclosures* instead.

## Notes on data schemas

If you publish structured results data, strongly prefer a stable public schema.
The NIST Election Results Reporting CDF is a well-known anchor reference for results data interchange and for avoiding bespoke, ambiguous formats.

