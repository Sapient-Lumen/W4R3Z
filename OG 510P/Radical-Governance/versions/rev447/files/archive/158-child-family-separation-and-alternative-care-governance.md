# Child–Family Separation & Alternative Care Governance (Anti‑Trauma / Anti‑Capture)

**Purpose:** make child protection decisions **rarer, narrower, reversible, and reviewable**—and ensure any separation is **time‑bounded, evidence‑based, and oriented to reunification** (unless clearly unsafe).

**Person served:** the child, their family/kin, and frontline caseworkers who need a system that **prevents unnecessary removal**, avoids institutional harm, and produces contestable records.

**From-below:** a child/family should be able to see (and contest) **why** separation happened, **what must happen next**, and **when** reunification will be evaluated.

---

## Kernel anchors (do not repeat)
- Decision receipts + reason codes + remedy lanes: `52-reason-codes-registry.md`, `36-appeal-lanes-and-redress-registry.md`, `66-justice-and-administrative-justice-governance.md`.
- Exception control / emergency powers discipline: `112-exception-control-and-emergency-powers.md`.
- Audit/inspection integrity + follow‑through: `130-audit-and-inspection-integrity.md`, `55-oversight-findings-and-response-register.md`.
- Data governance & privacy interfaces (minimize harm; correction lane): `127-data-governance-and-privacy-interfaces.md`.

## Named tensions
- **Safety vs trauma:** the system must prevent harm *and* avoid preventable separation harms (toxic stress, attachment disruption).
- **Speed vs correctness:** urgent protection is sometimes needed, but “fast” must still be **logged, reviewable, and time‑boxed**.
- **Professional discretion vs capture/bias:** discretion is necessary; unstructured discretion is how bias and quota‑like incentives enter.
- **Confidentiality vs accountability:** protect children’s data while still enabling **auditable** decisions and remedy.

---

## Non‑negotiable invariants (policy → interface)
1) **Family unity presumption**: separation is the exception, not the baseline (CRC “best interests” constraint; separation only when justified). See [BIB-UNCRC] and [BIB-CRC-GC14].
2) **Necessity + least‑intrusive test**: if safety action is required, choose the least intrusive measure that achieves protection, and record why alternatives were insufficient. See [BIB-ALTCARE].
3) **Kinship-first, institution-last**: prioritize family support and kinship/community care; avoid institutionalization except where strictly necessary and time‑boxed. See [BIB-ALTCARE] and [BIB-UNICEF-DEINSTIT-2024].
4) **Reunification orientation**: every separation decision carries a **reunification plan**, measurable supports, and a review clock—unless a documented safety threshold forbids it. See [BIB-ALTCARE].
5) **Contestability by design**: every removal/separation produces a **Separation Decision Receipt** with rights, deadlines, evidence ladder, and remedy lanes (including emergency hearing escalation).

---

## The Separation Decision Receipt (SDR)
Treat removal/separation like a high‑harm administrative action: it must produce a **receipt**.

**SDR minimum fields**
- **Trigger & authority** (who acted, legal basis, emergency/standard lane).
- **Claimed harms & evidence ladder** (what is alleged; what evidence supports it; confidence level; missing evidence).
- **Alternatives considered** (support services, in‑home safety plan, supervised contact, temporary kin placement).
- **Least‑intrusive justification** (why this measure and not a less intrusive one).
- **Placement type** (kinship / foster / residential) + **why**.
- **Contact plan** (visitation schedule, communications access, supervised/unsupervised rationale).
- **Reunification conditions** (what must change, supports promised, responsible agency, deadlines).
- **Review clock** (first review within X days; recurring reviews; maximum duration before escalated scrutiny).
- **Appeal & support** (legal aid / advocate access; translation; disability accommodations).
- **Data handling** (what’s recorded; who can see it; correction process; retention limits).

**Why receipts matter:** they prevent “silent” separation, reduce arbitrary practice variation, and create auditability without exposing sensitive details publicly.

---

## Lanes & clocks (make speed and review explicit)
A high‑integrity system exposes lanes and clocks rather than hiding them.

### Lane A — Immediate safety intervention (emergency)
- **Time‑boxed authority** (hours/days, not weeks).
- **Automatic independent review** scheduled at creation (no discretionary “we’ll see”).
- **Mandatory reason‑codes** for emergency use (prevents normalization of emergency lanes).  
Link to `112-...` (Four Locks) and `45-emergency-measures-register.md`.

### Lane B — Standard protection plan (non‑emergency)
- Requires a **documented alternatives attempt** (family supports offered, service availability constraints logged).
- Separation requires showing why **in‑home plan** or **kinship supports** cannot work.

### Lane C — Long‑term placement / parental rights termination (irreversible-ish)
- Requires **higher proof thresholds**, stronger representation access, and multi‑party review (judicial + child advocate).
- Must produce a **Benefits/Harms Forecast Receipt** (BHR) that includes expected trauma costs and service supports.

---

## Anti‑capture primitives (stop perverse incentives)
1) **No quota‑like incentives:** prohibit numeric targets for removals/closures; audit for proxy incentives (see `03-metrics-and-evidence.md` + `142-metrics-and-indicators-integrity.md`).
2) **Service scarcity disclosure:** if a safer alternative is unavailable (e.g., family support, housing, treatment), the SDR must record “*resource constraint*” explicitly—so the polity sees when removal substitutes for missing services.
3) **Bias checks with repair loop:** track disparate impacts with a **pattern remediation lane** (`76-systemic-redress-and-pattern-remediation.md`), not just dashboards.
4) **Independent child advocate access:** guaranteed and funded; conflicts-of-interest joins (`120-...`) when providers also evaluate.

---

## Data & record discipline (privacy + accountability)
- Maintain a **sealed case file** with cryptographic integrity logs (see `53-publication-integrity-and-tamper-evident-logs.md`), and publish only **aggregate, privacy‑preserving** statistics.
- Provide families a **case‑file access receipt** (who accessed what, when) consistent with `127-data-governance-and-privacy-interfaces.md`.
- Ensure portability for cross‑jurisdiction continuity (placement moves shouldn’t reset rights). See `109-portability-and-cross-jurisdiction-continuity.md`.

---

## Minimal registers (tight, implementable)
- **Separation/Removal Register** (non‑public; hashed pointers; lane + clock status).
- **Placement Capacity & Quality Register** (kinship/foster/residential; inspections; incident history). Link to `130-...`.
- **Family Support Service Catalog** (what supports exist; wait times; eligibility; denial receipts). Link to `47-service-catalog-and-access-journeys-register.md`.
- **Reunification Plan Register** (commitments, deadlines, missed obligations, reason codes).

---

## Governance tests (add to the test suite)
Add these checks to `107-governance-test-suite.md`:
- **No‑receipt test:** Can any child be separated without an SDR? If yes, fail.
- **Clock test:** Do emergency separations automatically schedule independent review? If no, fail.
- **Alternatives test:** Are alternatives logged and auditable? If no, fail.
- **Institution test:** Are residential placements time‑boxed with higher scrutiny? If no, fail.
- **Resource‑constraint visibility:** Do SDRs surface when separation substitutes for missing supports? If no, fail.

---

## Evidence docket (keys)
- CRC best‑interests duty and constraints: [BIB-UNCRC], [BIB-CRC-GC14].
- UN Guidelines for Alternative Care (necessity, suitability, family/kin priority): [BIB-ALTCARE].
- UNICEF synthesis on deinstitutionalization / keeping families together: [BIB-UNICEF-DEINSTIT-2024].
