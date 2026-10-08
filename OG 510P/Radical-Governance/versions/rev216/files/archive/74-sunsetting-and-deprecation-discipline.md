# Sunset, Deprecation, and Decommissioning Discipline (Keep Power Reversible)

**Purpose:** force periodic review and expiration so rules/programs can’t persist by inertia after they fail or harm.

Complexity is a capture vector: once rules/programs/systems accumulate, they become harder to understand, harder to contest, and easier to hide inside. “Sunset by default” is how you keep governance **small, legible, and reversible** without relying on permanent heroics.

This memo defines a **minimal, joinable lifecycle protocol** for retiring or renewing power (rules, programs, authorities, standards, and systems) using existing artifacts (`DRR`, `RULE`, `PROG`, `REL`, `OFR`, `AC`, `AL`, etc.).

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** disclosure and controls can be weaponized or ignored; design for safety and incentives. (`99-protective-legibility-and-adoption-dynamics.md`)
- **From-below usability:** these artifacts MUST remain comprehensible and actionable via the person’s path (assisted/offline options; no insider knowledge). (`98-persons-path-and-accessibility-invariants.md`)
- Rules/instruments and version pinning: `39-...`, `27-...`.
- Program register (evaluation + lifecycle): `28-...`.
- Publication integrity (“as-of” access for old rules): `53-...`.
- Interop obligations when interfaces change: `70-...`, `71-...`.

## Named tensions (design must surface these)
- Stability for reliance vs deprecation for safety and adaptation.
- Sunsetting bad instruments vs entrenchment through “temporary” exceptions.
- Backward compatibility vs clean breaks (complexity budget).
- Local discretion to extend vs central discipline to retire.

---
## A. Bright lines (when lifecycle discipline is mandatory)

Lifecycle discipline (explicit review clock + renewal/retirement artifacts) is **MUST** when any of the following hold:
- **High-discretion power:** coercion/custody, emergency authority, high-stakes ADS, critical infrastructure operations (see `73-...`, `05/06/23/59`).
- **High spend / fiscal tail-risk:** subsidies/tax expenditures, guarantees, PPPs/SOEs, large conditional transfers (see `07/18/49`).
- **Rule complexity / broad coverage:** major regulatory regimes or “rules as code” that affect large populations (see `39`, `13`).
- **Cross-boundary delegation with weak exit:** compacts and supranational regimes where local remedies are thin (see `19/50/60`).

**Rule of thumb:** if the downside is large, the default must be **time-bounded authority** with evidence-gated renewal.

---

## B. The minimal lifecycle artifact pipeline (no new ID families)

### 1) Set the review clock at creation
Any new or materially expanded rule/program/authority/system MUST publish:
- a **review date** (when we must reconsider), and
- a **renewal standard** (what evidence/thresholds are required), and
- a **continuity floor** (how ongoing cases/benefits/services are protected during transitions).

Use existing homes:
- rules: PRR fields (`39-...`),
- programs: `PROG-*` + `EVAL-*` commitments (`28-...`),
- exceptional measures: `EMR-*` sunsets (`45-...`),
- high-discretion regimes: `AC-*` stop/review triggers (`73-...`).



### 1b) Write a tiny review packet *now* (so review is possible later)

A review fails when the evidence wasn’t planned for. For any high-impact `RULE-*` / `PROG-*` / `AC-*`, the creator SHOULD publish a one‑screen **review packet** (as a `REL-*` pointer bundle) that includes:

- **Objective + theory of change:** what problem is being solved, for whom, and what “success” means (3–7 bullets).
- **Key metrics (3–10):** include at least one *distributional* metric and one *operational* metric (backlogs, error rates, time-to-remedy).
- **Assumptions + risk acceptance:** any nontrivial assumption or safety trade-off, with a review trigger if it fails.
- **Enforcement / burden signals:** audit rate, reversal rate, admin burden indicators, and “false positive” / “false negative” risks where applicable.
- **Remedy health:** the primary `AL-*` lane(s) and the current/target time-to-first-response and time-to-decision.
- **Review standard:** what evidence threshold is required to renew (and what evidence is sufficient to retire/replace).

This keeps the archive’s discipline: **the packet is pointers (IDs), not annexes**.


### 2) Renewal or retirement is a Decision Receipt
Renewal/termination MUST emit a joinable **Decision Record/Receipt**:
- **Renewal:** `DRR-KIND: REVIEW` (or `DEC`) citing: `RULE`/`PROG`/`AC`/`EMR` as applicable, plus the evidence docket (`REL/EVAL/OFR`).
- **Retirement / repeal / termination:** `DRR-KIND: NOTICE` (or `DEC`) citing the object being retired, effective date, and remedy lane(s) for transition disputes (`AL-*`).

**Non-negotiable:** renewals and terminations are not “press releases” — they are joinable `DRR-*` artifacts.

### 3) Publication must update the canonical registers
- **PRR:** update `RULE` status (in force → repealed/suspended) and keep tombstones resolvable (`39-...`).
- **Program register:** update `PROG-*` status and link the renewal/termination `DRR` and any `EVAL-*` result (`28-...`).
- **Standards register:** publish pinned version transitions and deprecation windows (`27-...`).
- **ADS/DPR registers:** model/system retirement updates, including who is responsible for residual appeals (`42-...`, `33-...`).

### 4) Missed reviews are governance incidents
If a review date passes without renewal/retirement artifacts, treat this as a **legibility failure**:
- open an `OFR-*` case (`CASE-TYPE: LEGIBILITY-GAP`) and publish a remediation deadline (`32-...`, `55-...`).
- allow `AL-LEG` complaints where missing lifecycle artifacts block contestation (`08-...`, `36-...`).

---

## C. Deprecation (replacement without breaking rights)

Deprecation means “this stays resolvable and appealable while we migrate.” Minimum requirements:

**1) Deprecation notice (`DRR-KIND: NOTICE`)**
- cites the retiring object (`RULE`/`STD`/`ADS`/`SRV`/`IDN`),
- names the replacement object(s),
- sets an overlap window and final sunset date,
- states what changes for people (fees, eligibility, enforcement, deadlines), and
- names the remedy lane(s) for transition disputes.

**2) Crosswalks and continuity**
- **Rules:** publish a compact “old→new” mapping for materially changed obligations.
- **Services:** update `SRV-*` journeys to prevent channel exclusion during migration (`47-...`).
- **Appeals:** lane crosswalk (old→new) and “no one loses an appeal right by migration” rule (`36-...`).

**3) No orphaned cases**
Ongoing cases MUST remain reviewable under a defined basis:
- either the old rule remains in force for pending matters, or
- a defined transition rule is published in PRR with an effective window.

---

## D. Decommissioning systems (especially digital)

Decommissioning is where silent harm occurs: lost records, broken appeals, “missing” evidence, and untracked data copies.

**Minimum decommission plan (publish as a short `REL-*` release and link it from the retirement `DRR`):**
- **Records continuity:** where authoritative records move; how retrieval works post-sunset (`31-...`).
- **Appeal continuity:** which lane hears legacy disputes and for how long (`36-...`).
- **Data retention and deletion:** what must be retained (legal/oversight) vs. what must be deleted, plus method notes. For media sanitization and disposal discipline, see [BIB-NIST-SP800-88R2-2025].
- **Vendor exit:** portability/escrow obligations, and post-termination audit rights (`38-...`).
- **Security/continuity:** how essential service continuity is preserved during cutover (`47-...`, `59-...`; continuity anchor [BIB-ISO-22301-2019]).

**Anti-theater check:** if the decommission plan cannot tell a person *where to get their records* and *how to appeal*, it is not complete.

---

## E. Authorities, compacts, and boundary changes (re-charter as a scope decision)

For authorities that can tax, regulate, or coerce (including special districts/SPVs), **re-charter is a scope decision**:
- re-charter/termination MUST emit `DRR-TYPE: SCOPE` (see `IOP-10` in `02-...`).
- the `DRR` MUST include: funding alignment, asset/liability disposition, remedy continuity, and a review trigger.

For compacts (`CMP-*`), renewals and exits MUST follow the compact’s own sunset/exit terms and publish continuity rules (`19-...`).

---

## F. Minimal metrics (portable)
Keep it small; publish as joinable `REL-*` releases.
- **Review completion rate:** % major `RULE`/`PROG` items with review completed on time ([REG-2]).
- **Staleness list:** count/list of items past review date (by ID, not narrative).
- **Renewal evidence coverage:** % renewals that cite a docket (`REL/EVAL/OFR/AC`) rather than assertions.

---

## Sources / anchors (keep tight)
- Regulatory review / ex-post discipline: [BIB-OECD-RPG-0390]; [BIB-OECD-STOCK-REVIEW-2020]; [BIB-OECD-RPO-2025].
- Post-implementation review / better regulation examples: [BIB-UK-BRF-GUIDE-2023]; [BIB-EU-BR-TOOLBOX-2023]; [BIB-US-EO13563-2011].
- Evaluation practice (decision hooks for keep/revise/stop): [BIB-UK-MAGENTA-2025].
- Continuity discipline (cutovers and essential services): [BIB-ISO-22301-2019].
- Media sanitization for system decommissioning: [BIB-NIST-SP800-88R2-2025].
