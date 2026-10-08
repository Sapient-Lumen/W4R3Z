# 261. Public commitments and transparency logs for election evidence

**Track:** Shared

This doc proposes a **thin, reusable pattern** for publishing **tamper-evident public commitments** (hashes + metadata) to election-related evidence artifacts **without publishing the artifacts themselves**.

The goal is to make “what existed when” independently checkable, while keeping:
- **voter privacy** (no ballot images, no per-voter records, no PII);
- **operational security** (no sensitive configs, credentials, or exploitable detail);
- **anti-weaponization posture** (avoid creating “how to interfere” instructions).

This is deliberately **digest-first**. It composes with:
- ENR Snapshot Packs (`252-...`)
- Change-control packets (`256-...`)
- Incident reporting digests (`259-...`)
- Audit Publication Packs / RLAs (`260-...`)

---

## Concept: public commitment ≠ disclosure

A **public commitment** is a small record that binds an actor to a statement like:

> “As of time T, we assert that object X existed with hash H, produced under procedure P, and we will later disclose it to authorized reviewers if required.”

Commitments are useful because they:
- deter *silent edits* (you can’t later swap X without changing H),
- enable third-party monitoring (watch for unexpected changes),
- support bounded public communication (publish the commitment even when disclosure is delayed or restricted).

---

## Core pattern: CommitLog Entry (CLE)

A **CommitLog Entry (CLE)** is a structured record published to one or more public channels.

**CLE fields (minimal):**
- `cle_id` (unique stable identifier)
- `object_kind` (e.g., `hfv.enr.snapshot_pack`, `hfv.audit.publication_pack`, `hfv.change_control_packet`)
- `sha256` (or stronger; include algorithm)
- `created_at` (timestamp)
- `authority` (issuing office/entity)
- `procedure_ref` (pointer to the relevant procedure doc / policy declaration)
- `scope` (what contest/jurisdiction/time range the object pertains to — **coarse only**)
- `disclosure_policy` (who can get full object later + how)
- `notes` (bounded; “known/unknown” style)

**Do not include:**
- ballot-level or voter-level data,
- device identifiers that could enable targeting,
- internal network topology, credentials, or configuration detail.

---

## Why append-only transparency logs help

Publishing CLEs to ordinary channels (web page, PDF, press release) is good. Publishing them to an **append-only transparency log** can be better because it supports:
- **inclusion proofs** (“this entry is in the log”),
- **consistency proofs** (“the log didn’t rewrite history”).

This is the same general idea used by Certificate Transparency logs (RFC 6962).  
See: RFC 6962 (CT) and background summaries.  
- xref: rfc6962_html
- xref: mdn_en_us_docs_web_security_defenses_certificate_transparency

For software supply chain integrity, similar “record signed metadata to an immutable ledger” ideas appear in Sigstore’s Rekor transparency log and in-toto attestations:
- Rekor overview: xref: sigstore_rekor_overview
- Rekor project: xref: github_sigstore_rekor
- in-toto specs: xref: intoto_specs_html

**Important:** election evidence logging must be more conservative than typical software transparency:
- publish **hashes and coarse metadata only**;
- never publish per-ballot information;
- never publish operational details that increase attack surface.

---

## Minimal deployment options (from lowest to highest complexity)

1. **Static public page + hash ladder**
   - Publish CLEs as a signed PDF or a static HTML page (and keep historical versions).
   - Include a “hash ladder” that chains each release to the prior release.

2. **Independent multi-publisher mirroring**
   - Have multiple parties (e.g., state + counties + partner orgs) mirror CLEs.
   - Divergence is a signal. This raises the cost of “quiet edits.”

3. **Transparency log integration**
   - Publish CLEs to a public append-only log, plus run independent monitors.
   - Treat monitor outputs as evidence objects (bounded, publishable).

This archive does **not** require adopting a specific log technology. The pattern is: **commitment + append-only history + independent verification**.

---

## Evidence surfaces

### A. Commitments you can publish almost always
- ENR Snapshot Pack commitment (hash + timestamp + non-finality language)
- Corrections log commitment (append-only)
- Canvass reconciliation ledger commitment (aggregate deltas)
- Audit Publication Pack commitment (randomness ceremony record hash; escalation record hash)

### B. Commitments you can publish with caution
- Change control / update packet hashes (no configs)
- Incident timeline digests (no investigative detail)

### C. Commitments you should generally avoid publishing
- anything that reveals exact physical security schedules,
- internal network diagrams,
- precise device serials mapped to locations,
- ballot-level artifacts (even hashed) if they can be linked to voter identity.

---

## Stop conditions (anti-weaponization)

Stop and route to `253-...` (PRR/retention bounds) + `249-...` (safe red teaming) if:
- someone requests logs or commitments that enable harassment, intimidation, or doxxing;
- publication would reveal sensitive locations/identifiers enabling targeting;
- publication would materially increase attack feasibility.

---

## External anchors (non-exhaustive)

These sources are cited for the *idea* of append-only logging and bounded publication, and for election-context ENR caution:
- RFC 6962 Certificate Transparency: xref: rfc6962_html
- MDN overview of CT: xref: mdn_en_us_docs_web_security_defenses_certificate_transparency
- Sigstore Rekor transparency log: xref: sigstore_rekor_overview and xref: github_sigstore_rekor
- in-toto attestation specs: xref: intoto_specs_html
- EAC ENR overview + securing checklist (context: unofficial results often perceived as final):
  - xref: eac_technology_estep_program_night_report_systems
  - xref: eac_enr_securing_results_checklist_pdf

