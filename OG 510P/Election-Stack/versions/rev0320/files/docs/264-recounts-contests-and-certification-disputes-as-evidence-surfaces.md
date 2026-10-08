# 264. Recounts, contests, and certification disputes as evidence surfaces

**Track:** Shared

This spec defines **bounded, publishable** “evidence surfaces” for the *post-election escalation lane*:
**recounts**, **administrative contests/challenges**, and **certification disputes**.

Goal: make the process **auditable and legible** to the public **without** publishing voter PII, enabling intimidation, or leaking sensitive operational details.

## Scope and non-goals

In-scope:
- Recount triggers (automatic/requested), scope, method, and custody boundaries.
- Administrative contest / challenge process (what is being claimed, by whom, under what authority).
- Certification disputes (what is paused, what is pending, what is still official vs unofficial).

Out of scope:
- Publishing per-voter or per-ballot data.
- Publishing operational “how to break it” details.
- State-by-state law tables (use `262-jurisdictional-policy-surface-registry.md` instead).

## Safety and minimization rules

**Hard bans (never publish):**
- Voter PII, ballot images, signatures, addresses, or any “traceable” chain linking voter→ballot.
- Detailed facility layouts, alarm/door systems, staff rosters, or shift schedules.
- Anything that would enable intimidation, harassment, or physical interference.

**Default posture:** publish **hashes + digests + process boundaries**, not raw artifacts.

## Core artifacts (publishable surfaces)

### 264.A — Recount Declaration (RCD)

A one-page public declaration:
- *Authority:* cite the controlling rule (jurisdiction reference in `262`).
- *Trigger type:* automatic threshold vs requested recount.
- *Scope:* contests included, precincts/ballot types included/excluded (only at high level).
- *Method:* hand recount vs machine retabulation vs hybrid (high level).
- *Custody posture:* “sealed / dual control / observed / logged” summary.
- *Public observation policy:* how observers may attend (constraints and non-interference).

Anchor references:
- EAC recount resources hub: https://www.eac.gov/election-officials/clearinghouse-resources-audits-recounts
- NCSL recount overview (jurisdiction variability): https://www.ncsl.org/elections-and-campaigns/election-recounts
- EAC EMG Quick Start: Conducting a Recount (PDF): https://www.eac.gov/sites/default/files/eac_assets/1/6/Quick%20Start-Conducting%20a%20Recount.pdf

### 264.B — Recount Chain-of-Custody Attestation (RCCA)

A bounded attestation (no sensitive internals):
- Seals used (types, not serial numbers if that’s sensitive locally), dual-control policy.
- Transfer log **digest** (hash of the internal ledger + timestamp + signer).
- Observation notes reference (see `250-observation-and-challenge-as-evidence-surfaces.md`).

### 264.C — Recount Tally Change Ledger (RTCL)

An append-only public ledger:
- “What changed?” at contest granularity:
  - before/after totals, deltas, and category of cause (reason codes only).
- Explicitly **not** a ballot-level audit trail.

If an RLA/tabulation audit is used, reference `260-*` Audit Publication Pack (APP) rather than reinventing.

### 264.D — Contest/Challenge Docket Digest (CCDD)

For administrative contests/challenges:
- Claim summary (bounded), filer identity class (candidate/party/observer/org) without doxxing.
- Authority channel (e.g., board hearing, court filing) and current status.
- A strict “what we know / what we don’t” field to avoid rumor amplification.

### 264.E — Certification Status Capsule (CSC)

A small public capsule, suitable for a website banner or press release:
- **What is unofficial** (ENR), what is **certified**, and what is **pending**.
- Which actions are paused (if any) and why (bounded).
- Next public update checkpoint.

Anchors:
- EAC overview of results/canvass/certification (2025): https://www.eac.gov/election-officials/election-results-canvass-and-certification
- EAC clearinghouse: results/canvassing/certification: https://www.eac.gov/election-officials/clearinghouse-resources-results-canvassing-certification
- CISA / NASS canvassing timeframes + recount thresholds resource: https://www.cisa.gov/resources-tools/resources/state-election-canvassing-timeframes-and-recount-thresholds

## Integration notes (where this plugs in)

- ENR snapshots & corrections: `252-election-night-reporting-and-unofficial-results-as-evidence-surfaces.md`
- Canvass reconciliation: `251-provisional-ballots-curing-and-canvass-as-evidence-surfaces.md`
- Audits/RLAs: `260-risk-limiting-audits-and-post-election-tabulation-audits-as-evidence-surfaces.md`
- Observation + challenge records: `250-observation-and-challenge-as-evidence-surfaces.md`
- Public commitments / transparency logs: `261-public-commitments-and-transparency-logs-for-election-evidence.md`
- Jurisdictional knobs and authoritative refs: `262-jurisdictional-policy-surface-registry.md`

## Stop conditions

Pause publication and route to counsel/security if:
- requests seek voter-identifying data, ballot images, signatures, or addresses;
- requests seek facility/physical-security details;
- publishing would materially increase intimidation or interference risk;
- dispute communications risk defamation or rumor amplification.

