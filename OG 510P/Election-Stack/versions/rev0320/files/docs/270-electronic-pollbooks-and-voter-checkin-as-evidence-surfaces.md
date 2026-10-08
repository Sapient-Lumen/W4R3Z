# 270 — Electronic pollbooks and voter check-in as evidence surfaces (integrity without voter-file leakage)

Electronic pollbooks (EPBs / e‑pollbooks) sit directly on the **front line** of in‑person voting: eligibility lookups, check‑in, ballot style assignment, and (often) real‑time synchronization across locations. They can fail *benignly* (queues) or *catastrophically* (incorrect issuance, duplicate crediting, outages that force “shadow” processes).

This module defines **publishable evidence surfaces** for EPB operations that improve public and auditor checkability **without** publishing voter data, precinct‑level sensitive internals, or operational details that could be weaponized.

Primary anchors (cite-first, do not import bulk):
- EAC (ESTEP): *Voluntary Electronic Poll Book Certification Requirements v1.0* (May 2024). https://www.eac.gov/sites/default/files/2024-05/Voluntary_Electronic_Poll_Book_Certification_Requirements_v1.0_508.pdf
- EAC (ESTEP): *Guidance for Pre‑Election Testing: Electronic Poll Books v1.0* (Jan 2025). https://www.eac.gov/sites/default/files/2025-01/ESTEP_EPB_Guidance_for_Pre_Election_Testing_v1.0.pdf
- EAC: *Electronic Poll Book Report* (Jul 2023). https://www.eac.gov/sites/default/files/2023-07/Electronic_Poll_Book_Report_Final_508.pdf
- NIST VTS: *Usability and Accessibility of Electronic Pollbooks* (Parts 1–3, 2023). Part 1 PDF: https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=957037
- CISA: Election security resource library (EPB-relevant hardening lives alongside broader election infra guidance). https://www.cisa.gov/topics/election-security/election-security-resource-library
- EAC: Voluntary Electronic Poll Book Certification Program overview (ESTEP EPBs). https://www.eac.gov/election-technology/estep-program/electronic-poll-books

## Goals and non-goals

### Goals
- Provide a **stable, minimal set** of artifacts that let observers answer: “Were EPBs operated competently and consistently?”
- Enable reproducible verification via **hash commitments** and **append-only digests**, not data dumps.
- Compose with:
  - `255-logic-and-accuracy-and-pre-election-testing-as-evidence-surfaces.md` (pre‑election testing)
  - `253-public-records-requests-retention-and-access-bounds.md` (records handling)
  - `265-canonicalization-signing-timestamping-and-proof-packaging.md` (CPP)
  - `261-public-commitments-and-transparency-logs-for-election-evidence.md` (CommitLog)

### Non-goals
- Publishing voter files, check‑in records, device identifiers tied to locations, or configuration details that would aid interference.
- Providing “how to attack EPBs” playbooks. This is an integrity-and-transparency module, not an exploitation guide.

## Minimal evidence surfaces (publishable artifacts)

Use **CPP** (`265-*`) for canonicalization + hashing + signing + optional timestamping; then publish commitments via **CommitLog** (`261-*`).

### EPB‑SPS — Electronic Pollbook System Posture Statement
A concise posture statement (1–2 pages) describing:
- EPB deployment model (centralized / local / hybrid), *at a coarse level*
- authentication approach (role-based; MFA posture), *no vendor secrets*
- connectivity expectations (offline/online modes; sync cadence), *no endpoints*
- contingency posture (paper backup, “failover rules”, escalation paths)

Publish: EPB‑SPS document + hash commitment.

### EPB‑CBA — EPB Configuration Baseline Attestation
Attests to:
- EPB software/version family and certification/qualification posture (where applicable)
- baseline configuration was frozen by a named role *class* (not individuals) by a deadline
- linkage to L&A / pre-election testing artifacts

Publish: attestation + hash; do **not** publish configs.

### PCD — Pre‑Check‑in Readiness Digest
A compact digest (counts-only) for:
- device inventory counts (by type), readiness checklist completion, spare units
- poll worker training completion counts (not names)
- pre-opening sync success rate and unresolved exceptions count

Publish: totals + exceptions summary + hash.

### CTLD — Check‑In Transaction Ledger Digest (aggregate-only)
An append-only daily digest that includes:
- check-ins by hour (bucketed) at jurisdiction level (or safely aggregated)
- “voter credited” events count
- provisional issued count and top-level reason codes (coarse categories)
- exceptions: overrides, manual entries, ID exception flow usage (counts only)

Publish: aggregated counts, and a hash chain across hourly/daily digests.

### BSA‑D — Ballot Style Assignment Digest
A digest proving that ballot style issuance followed the declared rules:
- counts of ballot styles issued (aggregated) + anomaly buckets (e.g., “style mismatch prevented”)
- any mid-day rule updates must reference a **Change Control Packet** (`256-*`)

Publish: aggregated counts + rule-hash reference (not mappings).

### SILD — Sync Integrity Ledger Digest
If EPBs synchronize across locations:
- number of sync cycles, success/failure counts, average latency buckets
- conflict counts and resolution policy reference (hash commitment to SOP)
- “offline issuance” periods count + duration buckets

Publish: totals + policy-hash references.

### OQC — Outage / Queue Capsule
When lines or outages exceed a threshold:
- timeline capsule (coarse timestamps)
- declared operational mode (offline, paper backup, curbside adaptations)
- recovery and reconciliation step pointer (where to verify next)

Publish: capsule + follow-up link to reconciliation digest.

## Reason codes (minimal dictionary)

Maintain a small **Reason Code Dictionary (RCD)** for check‑in exceptions and provisional triggers:
- stable codes, versioned
- any changes must be recorded in **CCP** (`256-*`) and committed via **CommitLog** (`261-*`)

Publish: the dictionary (safe), because it improves interpretability without exposing voter info.

## Stop conditions (privacy / ops / anti-weaponization)

Do not publish:
- any voter identifiers, partial identifiers, addresses, DOB, signature/ID images, or per-person check-in outcomes
- per-location device IDs, network details, endpoints, physical layouts, or precise staffing rosters
- precinct-level digests that enable targeted intimidation (“which precinct had X issue”)
- raw sync logs or crash logs containing internal topology

If a requester insists, route via:
- `253-public-records-requests-retention-and-access-bounds.md` (bounded access, redaction logs)
- and consult counsel / statutory requirements for the jurisdiction.

## Implementation notes (tight, practical)

- Prefer **aggregation tiers** that match public reporting norms (jurisdiction / county / district) and avoid “single site attribution.”
- Use **hash ladders** to connect: EPB‑CBA → PCD → CTLD/SILD → ENR snapshots (`252-*`) → canvass reconciliation (`251-*`) → audits (`260-*`).
- Treat usability as integrity: EPB usability failures create queue pressure and manual overrides. Use NIST VTS checklists as a *non-proprietary* evaluation anchor.

