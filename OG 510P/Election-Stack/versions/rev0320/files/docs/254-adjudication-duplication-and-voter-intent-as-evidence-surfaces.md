# Adjudication, Duplication, and Voter Intent as Evidence Surfaces

**Goal:** make *post-capture interpretation* (adjudication) and *ballot duplication/replication* checkable **without** enabling intimidation, doxxing, or “DIY recount” theater.

This doc defines **minimal publishable artifacts** for:
- **Adjudication** (review of voter marks / system exceptions)
- **Duplication / replication** (damaged/defective ballots copied to scannable format)
- **Voter-intent standards** (jurisdiction rules that guide interpretation)

It is intentionally *jurisdiction-agnostic*: rules vary widely. Use this as a **template** and bind it to your jurisdiction’s law, guidance, and procedures.

## Non-goals and hard stop conditions

Stop (do not publish; do not create “transparency” artifacts) if any proposal would:
- disclose **voter identity**, signatures, addresses, ballot images tied to identity, or traceable timestamps/batch IDs;
- reveal **sensitive operational security** details (camera angles, access controls, staff schedules, vulnerabilities);
- create a **playbook for interference** in adjudication/duplication operations;
- expand into **case-by-case** adjudication narratives that could be weaponized against voters or workers.

## External anchors

Use these as **citations**, not bulk imports:
- EAC **VVSG 2.0** (system behaviors + usability/verification expectations).
- NIST **Cast Vote Record (CVR) CDF** (how interpreted marks/choices can be represented and audited).
- CISA “**Voting System Security Measures**” (baseline secure operations posture).
- NCSL overviews of **voter intent laws** and **ballot duplication** (50‑state variance; vocabulary and common patterns).
- EAC **Guide to the Canvass** (where adjudication/duplication sit in the broader post‑election pipeline).

## The minimal publishable artifacts (MPA)

These artifacts should be publishable **without voter PII** and without enabling operational interference.

### MPA-254.A — Adjudication Policy Declaration (APD)

A one-page declaration (signed/dated) that states:
- what adjudication is **for** (resolving system exceptions / unclear marks per rules);
- who may adjudicate (roles, not names), required **dual control**, and escalation paths;
- the **voter-intent standard** used (statute/case law/manual reference);
- what is **not** adjudicated (e.g., no identity, no signature issues unless jurisdictionally required);
- what logs are kept and what can be published.

**Publishable proof:** APD PDF + hash + last revision date + authority citation.

### MPA-254.B — Adjudication Session Ledger (ASL)

An append-only ledger for each adjudication session:
- start/end time window (coarsened), location type (e.g., “central count facility”),
- roles present (e.g., “Adjudicator A/B”, “Observer liaison”), not names,
- number of exception items reviewed, disposition counts by reason codes,
- equipment identifiers at a **coarse** granularity (model/version cohort, not serials),
- references to batch IDs only if they are **non-traceable** externally.

**Publishable proof:** ASL summary table + hash; no per-ballot entries.

### MPA-254.C — Reason-Code Dictionary (RCD)

A short dictionary of adjudication reason codes that is stable over time, e.g.:
- “STRAY_MARK”, “OVER_VOTE”, “UNDER_VOTE”, “AMBIGUOUS_MARK”, “DAMAGED_BALLOT”
- for each: what it means, allowed dispositions, and required human review conditions.

**Publishable proof:** RCD file + hash; change log.

### MPA-254.D — Ballot Duplication Protocol (BDP)

If the jurisdiction duplicates ballots:
- when duplication is permitted (damaged/defective/read-failure),
- dual control, witness/observer posture,
- how originals are preserved and tracked (chain-of-custody),
- how duplicates are marked (e.g., “duplicate” indicator) and reconciled.

**Publishable proof:** BDP + a single-page flow diagram + hash.

### MPA-254.E — Duplication Reconciliation Summary (DRS)

Per election:
- count of ballots duplicated by reason category,
- reconciliation statement: originals secured; duplicates counted; totals match accounting rules.

**Publishable proof:** DRS + hash + linkage to the canvass reconciliation ledger.

## Privacy-preserving transparency patterns

- Prefer **aggregates** and **reason-coded counts** over per-item detail.
- If using ballot images for adjudication, do not publish them; instead publish:
  - the policy for image access,
  - access logs (role-based, coarse timestamps),
  - retention and deletion posture.

## Integration points in this archive

- Evidence minimization and assurance framing: `docs/246-*`
- Chain of custody + comms posture: `docs/247-*`
- Canvass and reconciliation surfaces: `docs/251-*`
- ENR/unofficial results snapshot patterns: `docs/252-*`
- Public records and access bounds: `docs/253-*`
- External anchors map: `docs/245-*`

## Checklist (one page)

- [ ] Adopt APD (signed, dated, cites authority)
- [ ] Define RCD (stable codes; change-controlled)
- [ ] Run ASL per session (append-only; publish aggregate summary)
- [ ] If duplicating ballots: adopt BDP + publish DRS per election
- [ ] Bind to canvass reconciliation and retention policies
- [ ] Confirm stop conditions (PII / security / intimidation risk)


## Primary anchors

- [EAC — VVSG 2.0 Requirements (PDF)](https://www.eac.gov/sites/default/files/TestingCertification/Voluntary_Voting_System_Guidelines_Version_2_0.pdf)
- [NIST — Implementation Guidance for Common Data Formats (GCR 24-058)](https://nvlpubs.nist.gov/nistpubs/gcr/2024/24-058/NIST.GCR.24-058.html)
- [CISA — Voting System Security Measures](https://www.cisa.gov/resources-tools/resources/voting-system-security-measures)
