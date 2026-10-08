# 260. Risk-limiting audits and post-election tabulation audits as evidence surfaces

**Track:** Shared

This doc defines a **publishable, privacy-first proof surface** for post-election tabulation audits—especially **risk-limiting audits (RLAs)**—that increases public checkability without dumping ballots, CVRs, or sensitive operational details.

We do **not** standardize a single audit method (jurisdictions vary). We standardize **what can be published safely** so observers, courts, media, and researchers can verify that an audit was real, bounded, and competently conducted.

External anchors (cite-first):
- EAC overview of audit types and variability.
- EAC Post‑Election Tabulation Audit Guide (2024).
- Lindeman & Stark “A Gentle Introduction to Risk‑Limiting Audits” (NIST / Berkeley versions).
- Verified Voting RLA explainers + method notes (public-facing).
- RLA implementation/documentation hub (examples + tools).

---

## Design goals

1. **Prove “audit happened”** (timing, scope, roles, randomness, custody) with minimal leakage.
2. **Prove “audit was bounded”** (risk limit / stopping rules / escalation) without publishing sensitive ballots.
3. **Prove “audit was repeatable”** (random seed, manifest commitments, method version, public hashes).
4. **Prevent weaponization**: no voter PII; no targeting of pollworkers/auditors; no instructions that enable interference.

---

## Core concept: Audit Publication Pack (APP)

Publish a compact, machine-readable + human-readable bundle (or PublicNotice links) that contains **only**:

### APP-0: Audit Declaration (AUDIT_DECL)
- Jurisdiction, election, contest(s) audited, audit type (RLA / fixed-percentage / procedural / tiered).
- Legal/policy authority references (jurisdiction-specific pointer).
- Timeline: start/end of each public step (seed ceremony, draws, pulls, interpretation, reconciliation, reporting).
- **Risk limit (if RLA)** and high-level method (ballot-polling vs comparison) with method version tag.

### APP-1: Scope Commitment (SCOPE_COMMIT)
- List of audited contests + reported margins (as-of canvass stage used).
- Audit trail type: voter-marked paper ballots / VVPR / other (declare limitations).
- Public statement of **what is *not* covered** (e.g., not a forensic device exam).

### APP-2: Manifest Commitment (MANIFEST_COMMIT)
- Hash of the ballot manifest (or batch manifest) used for random selection.
- Hash of any CVR export used for comparison audits (if applicable) **without** publishing the CVRs.
- Statement of reconciliation checks performed on the manifest’s completeness/accuracy (high-level).

### APP-3: Randomness Ceremony Record (RANDOMNESS_REC)
- Ceremony date/time/location class (not exact addresses if that increases risk).
- Participant roster (roles only by default; names optional).
- Seed source description (dice, RNG device, etc.) + **public seed value**.
- Hash of “draw input” file(s) used by the selection tool.
- Tool name/version + command synopsis (no sensitive paths).

### APP-4: Draw Output Digest (DRAW_DIGEST)
- Hash of the draw output list (ballot IDs / batch IDs as used operationally).
- Counts: number drawn, replacement rule if any, escalation logic summary.
- Link to **observer capture notes** pattern (`223`) if observers are present.

### APP-5: Chain-of-Custody Attestation (COC_ATTEST)
- “Ballots under seal / controlled storage” statement + custody roles.
- Any seal-break events summarized as anomalies (see `SURFACE_ANOMALY_CODES.md`), without granular physical security details.

### APP-6: Interpretation & Comparison Summary (INT_SUM)
- Aggregate counts of discrepancies by reason code (no per-ballot record).
- For comparison audits: aggregate overstatements/understatements summary (no mapping).
- Any ballot duplication/adjudication linkage uses the patterns in `254` (aggregate-only).

### APP-7: Stopping / Escalation Record (STOP_ESC)
- For RLAs: sample sizes by round, whether stopping condition met, and whether escalation occurred (up to full hand count).
- For non-RLAs: whether thresholds were met and what escalation path exists per policy.
- If escalation happened, publish a new APP revision (append-only).

### APP-8: Final Audit Report Digest (REPORT_DIGEST)
- One-page plain language “what we did / what changed / what didn’t change / why this builds confidence”.
- Hashes of any longer PDF report + any appendices hosted elsewhere.
- Pointer to canvass reconciliation surface (`251`) and ENR corrections log (`252`) if deltas exist.

---

## Publishable-proof matrix (tight)

| Claim | Publishable proof (bounded) |
|---|---|
| Random selection was not cherry-picked | Seed value + tool/version + hashes of manifest + draw inputs/outputs (APP-2/3/4) |
| Audit trail exists and was controlled | COC attestation + anomaly summaries (APP-5) |
| Audit checked the right scope | Audit declaration + scope commitment (APP-0/1) |
| Audit detected discrepancies & handled them | Aggregate discrepancy table + reason codes + escalation record (APP-6/7) |
| Public can track revisions | Append-only PublicNotice thread + hash ladder (see `220`, `221`, `226`) |

---

## Anti-bloat and privacy rules

**Do publish**
- Hashes, short digests, reason-code counts, high-level steps, tool versions.

**Do not publish**
- Ballot images, ballot IDs, batch storage locations, per-ballot interpretations, voter PII, pollworker home contact info.
- Detailed physical security layouts or schedules that enable interference.

If a records request demands sensitive details, route through `253-public-records-requests-retention-and-access-bounds.md`.

---

## Stop conditions (do not proceed without a new safety review)

1. Any request to publish **per-ballot** or **precinct-small** discrepancy details.
2. Any request to publish ballot storage locations, seal identifiers in a way that enables targeting, or staff schedules.
3. Any attempt to turn the audit pack into a “how to defeat audits” manual.

---

## Where this plugs in

- Lifecycle map: `215-election-lifecycle-evidence-map.md`
- Canvass / provisional / curing reconciliation: `251-...`
- ENR corrections + snapshot packs: `252-...`
- Adjudication / duplication surfaces: `254-...`
- Threat model ledger + safe red-teaming: `249-...`
- PublicNotice state resolution + monitoring: `220`–`223`


## Primary anchors

- EAC — Post-Election Tabulation Audit Guide (2024) (PDF) (xref: eac_post_election_tabulation_audit_guide_2024_pdf)
- NIST — A Gentle Introduction to Risk-Limiting Audits (xref: nist_gentle_intro_rla_pdf)
- Jennifer Morrell — Knowing It’s Right (Part 1) (PDF) (xref: democracy_fund_content_uploads_2020_06_2019_df_knowingitsright_part1)
