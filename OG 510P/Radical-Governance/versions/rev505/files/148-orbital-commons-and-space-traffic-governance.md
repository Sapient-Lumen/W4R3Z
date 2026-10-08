# Orbital Commons & Space Traffic Governance (Functional / Global Commons)

**Purpose:** treat near‑Earth orbit and cislunar space as a *commons with consequences*—preventing collisions, debris cascades, and unilateral enclosure while keeping exploration open.

**Person served:** any person harmed by downstream impacts of space activity (navigation failure, comms loss, debris re-entry risk, surveillance escalation) who needs *accountability that doesn’t vanish above borders*.

**From-below:** this memo turns “space is hard” into **traceable obligations**: who must do what, who pays, what data must be public, and what remedies exist when someone’s “oops” breaks the commons.

---

## 0. Baseline legal floor (what already exists)
Space governance is not a blank slate. It has a **thin but real** international legal spine:
- **Non‑appropriation + freedom of use/exploration** (no sovereignty claims) in the Outer Space Treaty. See [BIB-UNOOSA-OUTERSPACE-TREATY].
- **Responsibility / liability concepts**: states remain responsible for national activities, including by non‑governmental entities (Outer Space Treaty) and face liability regimes for damage. See [BIB-UNOOSA-OUTERSPACE-TREATY], [BIB-UNOOSA-LIABILITY-CONVENTION].
- **Object registration** expectations (who launched what; to reduce ambiguity). See [BIB-UNOOSA-REGISTRATION-CONVENTION].
- **Voluntary safety norms** for debris and long‑term sustainability (COPUOS). See [BIB-UNOOSA-SPACE-DEBRIS-GUIDELINES-2007], [BIB-UNOOSA-LTS-GUIDELINES-2019].

This archive’s goal is to **operationalize** those floors into institutions that can actually hold a commons together.

---

## 1. Threat model (why “orbit” is a governance problem)
**Primary failure modes:**
1. **Collision externalities** (conjunction risk imposed on others; incentives to free‑ride on others’ tracking).
2. **Debris cascades** (rare but catastrophic tail risks; “slow violence” to the commons).
3. **Registry opacity** (unclear ownership / responsibility; shell operators).
4. **Asymmetric power** (a few actors shape norms; others bear risk).
5. **Dual‑use escalation** (civil systems become strategic targets; norms collapse into security secrecy).

Design implication: treat orbit like an **ecological commons with safety‑critical operations**, not a frontier for “move fast”.

---

## 2. Minimal institution set (smallest stack that could work)

### 2.1 A federated Space Traffic Authority (STA) — functional, not sovereign
A *functional authority* that coordinates **traffic rules + data + incident response**, without territorial claims.
- **Mandate:** conjunction norms, transparency floors, incident investigations, and “unsafe operator” designation.
- **Structure:** polycentric / federated nodes (national agencies + regional consortiums) under a common rulebook; avoid single‑point capture.
- **Outputs (public):** safety directives, event notices, de‑identified post‑mortems, and operator scorecards.

Anchor to COPUOS sustainability guidance as the normative umbrella. See [BIB-UNOOSA-LTS-GUIDELINES-2019].

### 2.2 An enforceable registry (who is responsible)
Move from “registry as paperwork” to **registry as accountability interface**:
- **Required fields:** beneficial ownership, operator-of-record, insurer-of-record, maneuver capability class, end‑of‑life plan.
- **Receipts:** signed change logs for operator transfers and control delegation.
- **Portability:** cross‑jurisdiction handoff rules (avoid “flag of convenience” evasion).

Registration norms: [BIB-UNOOSA-REGISTRATION-CONVENTION].

### 2.3 Debris bonds + end‑of‑life proof (align incentives)
Licenses require posting a **debris bond** sized to risk class; refunds require *verified* disposal or passivation.
- **Default:** bond forfeiture finances remediation bounties / clean‑up procurement.
- **Proof:** telemetry + independent verification (auditable evidence, not promises).

Tie to debris mitigation expectations: [BIB-UNOOSA-SPACE-DEBRIS-GUIDELINES-2007], plus technical consensus (IADC). See [BIB-IADC-DEBRIS-GUIDELINES-REV2].

### 2.4 Incident investigation + liability routing (no “silent swap”)
Create a standard **space incident protocol** (SERIOUS INCIDENT lane):
- mandatory reporting windows
- independent investigation authority
- publication of a *minimum public* post‑incident record (redactions allowed but justified)

Liability framing: [BIB-UNOOSA-LIABILITY-CONVENTION].

---

## 3. Norms that should be made explicit (avoid norm drift)
These should be treated as *governance invariants*:
- **Non‑appropriation / no sovereignty-by-contract** (no “private treaties” that function as territorial claims). See [BIB-UNOOSA-OUTERSPACE-TREATY].
- **Open scientific access** to non‑sensitive results and environmental monitoring.
- **Heritage protection** (e.g., historically significant sites) via “protected zones” with transparent boundaries and review.
- **Safety data as public infrastructure**: baseline conjunction + debris environment data must not be paywalled for safety‑critical use.

---

## 4. Integration with the archive (where to plug in)
- Treat the STA as a **functional authority** (see `15-functional-authorities.md`) with a tight **competence ledger** (see `197-polycentric-federalism-and-overlapping-sovereignty.md`).
- Use the archive’s **evidence dockets** + **postmortem culture** from reliability engineering in `09-public-service-and-state-capacity.md` and `104-governance-control-loops.md`.
- Use `110-budget-procurement-integrity.md` for remediation procurement (avoid “cleanup capture”).

---

## 5. Practical “first releases” (low-regret steps)
1. **Minimum public registry schema** + signed change logs.
2. **Conjunction disclosure floor** (what must be shared, when, and with whom).
3. **Debris bond pilots** (small classes first; publish results).
4. **Incident protocol** for near misses + collisions (common vocabulary and reporting).

---

## Notes
This memo deliberately avoids proposing a “world space government”. The goal is **operational stability** via federated rules, transparent accountability, and incentive alignment—consistent with existing space law baselines and COPUOS guidance.
