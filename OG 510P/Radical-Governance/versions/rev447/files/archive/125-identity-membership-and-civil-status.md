# Identity, Membership & Civil Status (Treat Status as Power)

**Purpose:** make *civil status* (identity, membership, residency, eligibility) legible, contestable, and portable—so people cannot be silently excluded, duplicated, stranded, or “un-personed” by administrative seams.

**Person served:** someone whose access to rights/services depends on status (ID, residency, citizenship, eligibility) and who needs a *receipt* that can be used across agencies/jurisdictions.

**From-below:** status must never be a black box; every grant/denial/change must produce a usable receipt, a safe contest lane, and continuity during disputes.

## Threat model (why this exists)
- **Exclusion by friction:** “no ID” becomes “no service,” even when lawful alternatives exist.
- **Silent status drift:** residency/eligibility changes without notice; retroactive revocations.
- **Duplicate / fragmented identity:** multiple IDs across systems; inconsistent records; benefit cliffs.
- **Weaponized identity proofs:** impossible evidentiary demands; biased documentation norms.
- **Cross-jurisdiction cliff edges:** moving breaks care/benefits/standing; files “reset.”
(See also portability/continuity: `109-portability-and-cross-jurisdiction-continuity.md`.)

## Identity & status as interfaces (minimal primitives)

### 1) Status categories must be explicit
Define a minimal **Status Vocabulary** per domain: *what statuses exist, what they unlock, and what evidence is acceptable*.
- Publish a **Status Map**: `STATUS-{domain}-{code}` → effects, duration, and challenge lane.
- Publish a **Negative Space Policy**: what happens when status is *unknown* (default continuity vs default denial).

### 2) Civil Status Receipts (CSR-*)
Every status grant/denial/change produces a **Civil Status Receipt**:
- `CSR-id` (stable), person-facing summary, machine-readable core
- status claimed/changed (`STATUS-*`), effective date, expiry/review
- evidence used (with **record pointers**, not raw docs) and why it met the standard
- contest path (lane, deadline, cost/help), and portability notes (what transfers)
- **continuity default** while contested (what remains in force; what is paused)
(Use record/FOI + stable pointers from `115-information-integrity-and-record-interfaces.md`.)

### 3) Evidence floors (anti-impossible-proof)
For each status, publish an **Evidence Ladder**:
- “Best” evidence and at least **two** fallback routes (including *non-documentary* attestations)
- bias audit obligation (who lacks the “best” evidence and why)
- a hard rule: **no moving goalposts**—the required standard cannot change mid-case without a Rule Change Receipt (`118`).

### 4) Non-reset rule for transfers (continuity over seam)
When a person moves between agencies/jurisdictions:
- **Transfer cannot reset** standing, clocks, or evidence already accepted unless a written contradiction is issued.
- Use `CR-*` continuity receipts (`109`) + dispute lane `CRD-*` (`114`) when institutions disagree.
- Default to **provisional continuity** for essential services during verification (time-bounded).

### 5) “No-status-no-service” is not allowed for essentials
For essential services (health, shelter, safety, basic income floor), require:
- a **provisional access** lane with bounded fraud controls
- a staffed/non-digital path and a *help obligation* (see `98-persons-path-and-accessibility-invariants.md`).

## Accountability hooks (make identity power contestable)
- **Status Registry:** publish aggregate counts by status + transition rates (no personal data), plus backlog and error indicators.
- **Audit sampling:** use verifiable draws (`119`) for random case audits (bias + error).
- **Circuit breakers:** if denial rates spike, backlog breaches time budgets (`108`), or error rates rise → mandatory review + interim protections (`105`).

## Tests (portable, minimal)
- **Replayability:** from `CSR-*` + record pointers, can a third party reconstruct the basis for status?
- **Portability:** can a person move jurisdictions without losing continuity (provisional access works)?
- **Contestability:** can a person challenge status without specialist help (receipt is comprehensible; lane exists; clocks are real)?

## References (tight)
- Legal identity as an access enabler and rights issue: **[BIB-UN-SDG-16-9]**.
- CRVS / foundational identity systems and inclusion risks: **[BIB-WB-ID4D-CRVS]**, **[BIB-UNICEF-CRVS]**.
