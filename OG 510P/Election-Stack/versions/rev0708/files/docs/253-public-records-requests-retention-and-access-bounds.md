# 253. Public records requests, retention, and access bounds (publishable proofs without bloat)

**Track:** Shared

This doc defines a **minimal, privacy-first evidence surface** for responding to public records requests (PRRs) and related access demands **without**:
- leaking voter PII or sensitive security details,
- enabling intimidation / harassment,
- breaking chain-of-custody, or
- exploding the archive with bulk exports.

It also captures a minimal **retention posture**: what must be preserved, and how to prove preservation **without** publishing the preserved material.

## 1) Core principles

1. **Transparency is not raw-data maximalism.** Prefer *procedures + logs + hashes + reproducible selection rules* over bulk disclosure.
2. **PII and sensitive security details are non-negotiable exclusions** unless a lawful process compels disclosure, and even then: minimize.
3. **One-way accountability:** publish what you can safely publish; retain what you must retain; be able to prove you did both.
4. **Append-only corrections discipline:** response packets can be superseded, never silently replaced.

## 2) Threat model (PRRs as an attack surface)

PRRs may be used to:
- exhaust staff capacity (volume / ambiguity),
- fish for sensitive info (equipment configs, network diagrams, credentials, voter PII),
- obtain artifacts to fuel misinformation,
- demand “forensic access” to equipment in ways that endanger integrity.

EAC’s PRR best practices are explicit that election offices have faced increased PRR volume and need scalable handling patterns.  
Anchor: EAC “Best Practices: Public Records Requests” (PDF + landing page).  
- xref: eac_electionofficials_public_records_requests_best_practices_508
- xref: eac_officials_best_practices_public_records_request

Also see security framing on access to records/equipment (Brennan Center):  
- xref: brennan_center_research_reports_responsibilities_officials_regarding_acc

## 3) Minimal publishable artifacts (do not publish the records themselves)

### 3.1 PRR log (publishable summary)
Publish a rolling, privacy-safe **PRR log** (weekly/monthly) with:
- request ID, received date/time, scope category tag(s), disposition (fulfilled/denied/partial), completion date
- time-cost estimate bucket (e.g., S/M/L)
- **redaction reason tags** (not the redacted data)
- whether request sought equipment access (Y/N)

No requester names; no addresses; no case details.

### 3.2 Response packet (publishable)
For each PRR, publish a small **ResponsePacket**:
- request ID + scope tags
- a short statement of what was provided (high-level)
- what was withheld and why (category tags)
- links to already-public materials
- **hashes** of files that were produced (if lawful to disclose the hashes)
- a pointer to the jurisdiction’s appeal process (link, not prose)

### 3.3 Redaction log (publishable)
If redaction occurs, publish a **RedactionLog** referencing:
- input artifact hash
- output artifact hash
- transformation class (e.g., PII removal, security-sensitive removal)
- authority tag (FOIA exemption / state category tag / “security-sensitive”)

(See also: `225-redaction-logs-and-transformation-accountability.md`.)

### 3.4 Access demand log (equipment / facilities)
Publish an **AccessDemandLog** (summary) for requests that seek:
- physical access to voting equipment,
- imaging of storage media,
- direct “forensic” analysis,
- access to ballots outside statutory processes.

Include disposition and safety rationale category tags (chain-of-custody, threat to integrity, etc). Do not describe technical details.

## 4) Retention posture (minimal, cite-first)

### 4.1 Federal floor: preserve election records (where applicable)
U.S. federal law requires certain election records be retained and preserved for a period (commonly referenced as **22 months** for elections involving federal candidates).  
Anchor: 52 U.S.C. §20701 (and Chapter 207).  
- xref: uscode_house_num_0_req_granuleid_usc_prelim_title52_section20701
- xref: uscode_house_xhtml_edition_prelim_path_prelim_title52_subtitle2_chapter2

State/local requirements may add additional retention rules; treat them as overlays.

### 4.2 How to prove retention without publishing retained materials
Publish a **RetentionAttestation** for each election:
- what categories are retained (taxonomy only),
- retention window(s) (date bounds),
- custodian-of-record role (not a person),
- storage posture (offline/online, encryption-at-rest, access controls category),
- **inventory hashes** (hash of a manifest of retained items, not the items)

This creates a durable proof surface without leaking content.

## 5) Safe defaults and stop conditions

Stop conditions (escalate to counsel/security review):
- requester demands voter PII, signature images, or individualized ballot details
- requester seeks equipment access beyond lawful observation/audit processes
- request would require publishing security-sensitive configurations, network diagrams, or credentials
- request is entangled with active litigation or ongoing incident response

When in doubt, treat as **safety + integrity** review, not as a “data dump” project.

## 6) Integration points in this archive

- Ops controls + comms discipline: `247-ops-security-controls-comms-and-chain-of-custody.md`
- Observation/challenge logs: `250-observation-and-challenge-as-evidence-surfaces.md`
- Canvass reconciliation discipline: `251-provisional-ballots-curing-and-canvass-as-evidence-surfaces.md`
- ENR snapshots + corrections logs: `252-election-night-reporting-and-unofficial-results-as-evidence-surfaces.md`
- Redaction accountability: `225-redaction-logs-and-transformation-accountability.md`
- Evidence minimization: `246-assurance-case-skeleton-and-evidence-minimization.md`

