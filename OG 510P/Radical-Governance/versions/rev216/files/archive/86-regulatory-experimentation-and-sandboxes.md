# Regulatory experimentation and sandboxes (Discipline)

**Purpose:** enable learning-by-doing without turning pilots into rights erosion or unaccountable deregulation.

“Try it” is not a governance plan unless the trial is **bounded, supervised, and learnable**.

This memo defines the minimal discipline for **live testing** (pilots, sandboxes, living labs) where a public authority allows constrained operation **under modified or relaxed conditions** to generate evidence and reduce uncertainty.

**Core rule:** no experimentation without (1) **a stop condition**, (2) **a receipt for every departure**, and (3) **a public learning artifact**.

Related:
- `85-waivers-variances-and-exceptions-discipline.md` (every sandbox admission is an auditable exception)
- `74-sunsetting-and-deprecation-discipline.md` (expiry is default; renewal must be justified)
- `28-program-register-and-evaluation-commitments.md` (program + evaluation spine)
- `73-assurance-case-and-governance-safety-case.md` (if high-risk, prove why it’s safe enough)

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** disclosure and controls can be weaponized or ignored; design for safety and incentives. (`99-protective-legibility-and-adoption-dynamics.md`)
- **From-below usability:** these artifacts MUST remain comprehensible and actionable via the person’s path (assisted/offline options; no insider knowledge). (`98-persons-path-and-accessibility-invariants.md`)
- Program register + evaluation commitments: `28-...`.
- Waivers/exceptions discipline: `85-...`.
- Assurance cases for safety claims: `73-...`.
- Records/publication integrity for learnings: `31-...`, `53-...`.

## Named tensions (design must surface these)
- Innovation and learning vs capture and deregulatory laundering.
- Experiment speed vs harm to participants/third parties.
- Local trials vs systemic fairness (who bears risk; who gains).
- Transparency of results vs trade secrets and strategic behavior.

---
## A. When this tool is appropriate
Use experimentation/sandboxes when:
- you need **live testing** to answer a policy question (simulation/analysis is insufficient),
- the potential public value is meaningful, and
- you can **supervise + remediate** harms during the trial.

Do **not** use a sandbox when:
- the authority cannot monitor and enforce constraints in real time,
- the trial would predictably cause serious rights violations, coercion, or irreversible harms,
- the “pilot” is a disguised path to permanence (no intention to publish results or update rules),
- the real need is ordinary rulemaking, guidance, procurement reform, or enforcement.

---

## B. Minimal artifact spine (reuse existing IDs)
A sandbox is a **program + a controlled set of exceptions**.

### B1) Sandbox program record (`PROG-*`)
Register the sandbox as a `PROG-*` (see `28-...`). This makes sponsorship, scope, and learning commitments joinable.

Minimum fields to include:
- **Objective + hypothesis:** what uncertainty is being reduced; what would change if the hypothesis fails.
- **Scope + boundary:** who/where is in-bounds; what is out-of-bounds.
- **Rule deltas:** which `RULE-*`/`STD-*` requirements are relaxed and why.
- **Eligibility + selection:** criteria; anti-favoritism controls; publication of selection rationale.
- **Protections:** compensation/insurance/bonding; complaint/appeal lane(s) (`AL-*`).
- **Monitoring:** live metrics (`GATE-0`) + reporting cadence; incident reporting requirement.
- **Stop conditions (“kill switches”):** triggers that pause/terminate tests.
- **Data governance:** what data is collected, retained, shared; privacy floor.
- **Exit + scaling path:** graduation criteria; what rule update is required to generalize.
- **Sunset:** default expiry date and maximum extension rule.

### B2) Admission / derogation receipts (`DRR-*` tagged `DRR-TYPE: EXCEPTION`)
Each participant/test MUST emit a receipt that states:
- the exact departure (what requirement is relaxed),
- the legal basis,
- bounds (time, geography, user caps, product/service caps),
- required safeguards + reporting,
- the contestation lane(s) and who is liable.

**No silent extensions:** renewals/revocations are new receipts.

### B3) Learning releases (`REL-*`)
At minimum, publish a cohort/phase closeout as a `REL-*`:
- what was tested (high level),
- what was learned (including negative results),
- incidents and how they were handled (with lawful redactions),
- whether rules will change, and why.

If details must be withheld, publish **existence metadata** (that a test happened, dates, sponsor, and next review).

---

## C. Operating discipline (how to keep it safe-to-fail)

### C1) Governance separation (avoid “regulator-as-accelerator” capture)
- The authority can clarify requirements, but SHOULD NOT provide privileged help that functions as a market advantage.
- Publish selection/eligibility rationales; apply `79-...` conflict-of-interest discipline.

### C2) Harm containment
For any test with real users:
- pre-commit to compensation/recourse; make the remedy lane obvious (`36-...`, `76-...`).
- require incident reporting into the relevant register (`INC-*`/`AL-*`/domain incidents).
- impose caps (users, exposure, geography) and enforce them with verification (`81-...`).

### C3) “Pilot → permanent” is not allowed without rule change
Scaling or generalization MUST:
- update the relevant `RULE-*`/`STD-*` and publish a rationale receipt, or
- terminate and publish the learning release.

A sandbox is a learning instrument, not a parallel shadow-regime.

---

## D. Exit discipline (closure is the point)
Every test exits with one of:
- **Graduate:** move to ordinary compliance + any needed `RULE-*` updates.
- **Terminate:** publish why; capture lessons; compensate as needed.
- **Extend (rare):** one bounded extension with explicit reason + updated stop conditions.

Missing closeout artifacts are **incidents**.

---

## E. Design references (for deeper practice details)
- `[BIB-OECD-REGEXP-2024]` (taxonomy + governance requirements for regulatory experimentation)
- `[BIB-OECD-SANDBOX-TOOLKIT-2025]` (implementation toolkit)
- `[BIB-CGAP-WB-SANDBOX-2020]` (practical design/ops guidance + alternatives)
- `[BIB-FCA-SANDBOX-LESSONS-2017]` (early lessons learned)
