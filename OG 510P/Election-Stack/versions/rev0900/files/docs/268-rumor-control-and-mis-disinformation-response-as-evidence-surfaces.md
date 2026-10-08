# 268 — Rumor control and mis/disinformation response as evidence surfaces

**Track:** Shared

This spec defines a *bounded*, privacy-first way to publish **verifiable public corrections** without turning the archive into a “fact-check site” or leaking sensitive operational details.

## Why this belongs in the Election Stack

Even with strong technical controls, the *legitimacy* of an election can be attacked through:

- **False procedural claims** (e.g., “polls are closed”, “machines are down”, “a court ordered X”),
- **Impersonation** of election offices and officials,
- **Selective-context media** (cropped video, synthetic audio),
- **Confusion attacks** (multiple unofficial “results” sources, contradictory instructions).

This module supplies *publishable evidence surfaces* that (a) are small and (b) compose with existing mechanisms:

- `200`–`206` PublicNotice feeds, parity snapshots, and digest cards
- `252` ENR snapshot packs + corrections logs
- `259` incident reporting and coordinated disclosure
- `261` CommitLog / transparency-log commitments
- `265` Crypto‑Proof Packaging (CPP)

## Non-goals / hard boundaries

- This archive does **not** adjudicate truth across political narratives.
- This archive does **not** publish voter PII, staff info, facility layouts, or actionable defensive gaps.
- This archive does **not** publish targeting data (precinct-by-precinct “problem maps”) that can be weaponized.

If a proposed “correction” requires naming private individuals, posting footage of voters, publishing addresses, or providing operational attack guidance, **stop** and route through the retention/PRR bounds doc (`253`) and legal counsel.

## Core pattern: RumorControlPack (RCP)

A **RumorControlPack** is a small, content-addressed packet that binds a correction to:

1. **A stable claim identifier** (CID)
2. **A minimal statement of fact** (the correction)
3. **A verification pointer** (where an independent verifier can check)
4. **A provenance chain** (who signed, when, and under what key policy)

### RCP minimal fields

- `cid` — deterministic claim ID (see below)
- `claim_summary` — one sentence, neutral wording
- `status` — `false` | `misleading` | `unverified` | `resolved` | `out_of_scope`
- `correction` — one sentence (what people should believe/do)
- `verification` — list of safe pointers (PublicNotice digest, statute reference, court docket link, hotline number, physical signage policy)
- `issued_at`, `expires_at` — explicit validity window
- `signatures` — CPP envelope signatures (see `265`)

**Evidence minimization:** the RCP should not embed screenshots, long text, or media. Instead, it should publish **hash commitments** to any supporting material and a recipe for independent verification.

### Claim identifier (CID)

A CID should be reproducible so multiple parties can refer to the same claim without coordination.

Minimal CID recipe:

- Normalize the claim to a short canonical string:
  - strip punctuation, lower-case, normalize whitespace
  - remove named individuals
  - avoid precinct/location granularity
- Compute `cid = sha256("rcp:v1:" + normalized_claim)`

## Publishable evidence surfaces

### 1) RumorControl index (RCI)

An append-only list of:

- `cid`
- `status`
- `rcp_digest`
- `issued_at`, `expires_at`

Publish the RCI as a **PublicNotice** surface so it’s easy to mirror and parity-check (`200`–`204`).

### 2) Corrections log interoperability

If the correction is about **unofficial results** or **reporting errors**, do *not* duplicate the entire story here.

Instead:

- publish an RCP whose `verification` points to the `252` **corrections log** entry (or `260` audit pack, or `264` dispute pack), and
- bind the relationship by including the referenced digest(s) in the RCP.

### 3) Synthetic media handling capsule (SMHC)

For suspicious audio/video/image:

- publish *only* a **capsule**:
  - `cid` (the claim)
  - authenticity posture: `unverified` / `verified_authentic` / `verified_inauthentic`
  - verification pointer: “only trust statements signed by X keys and posted at Y surfaces”

Do not publish technical forensic details that help an adversary refine forgeries.

### 4) “Where to verify” directory (WVD)

A small, durable directory of:

- official phone numbers (already public)
- official office URL(s)
- official social accounts
- official in-person signage policy

This composes with `203` (official channel directory). The WVD is a *human-first rendering* of the same commitments.

## Stop conditions (anti-weaponization)

Do not issue an RCP (or publish an RCI update) that:

- identifies private individuals,
- increases harassment risk,
- provides operational attack instructions,
- reveals security-sensitive schedules/locations,
- amplifies a claim whose only effect is attention.

When in doubt, publish a **process correction** ("Here are the only official channels; anything else is unverified") rather than repeating the rumor.

## External anchors (cite-first)

- CISA + EAC, *Enhancing Election Security Through Public Communications* (May 2024): practical guidance on election security communications. 
  - PDF: xref: eac_enhancing_election_security_public_comms_2024_pdf
- EAC + CISA, *Election Infrastructure Incident Response Communications Guide* (Oct 2024): how to communicate during incidents. 
  - PDF: xref: eac_incident_response_comms_guide_pdf
- Election Infrastructure GCC/SCC, *Rumor Control Page Start‑Up Guide* (implementation example for jurisdictions building rumor-control pages; xref context only, not current authority).
  - Link (public mirror): xref: iml_key_23626
- CISA election security resources hub (for jurisdiction-appropriate references and support channels):
  - xref: cisa_security
