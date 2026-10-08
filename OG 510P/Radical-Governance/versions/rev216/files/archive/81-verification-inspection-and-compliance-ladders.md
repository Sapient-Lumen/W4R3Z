# Verification, Inspection & Compliance Ladders (Trust but Verify)

**Purpose:** define verification and compliance ladders so enforcement is predictable, proportionate, and auditable.

Many governance failures are not about “bad rules” but **non-verified obligations**: actors can claim compliance while defecting, hiding, or gaming measures. This memo defines a compact **Minimum Viable Verification & Inspection spine (MVVI)** that plugs into the archive’s join-keys without creating a new bureaucracy tier.

**Use:** treaties/compacts, regulated industries, safety regimes, subsidies/conditionality, cyber baselines, public‑health capacities, climate commitments, and any program where success depends on **honest reporting** and **corrective action**.

**Anchors (high-trust examples):**
- Paris Agreement transparency framework MPGs (Decision 18/CMA.1): see [BIB-UNFCCC-ETF-MPGS].
- IAEA safeguards agreements + Additional Protocol (verification tooling + access rights): see [BIB-IAEA-SAFEGUARDS-AGREEMENTS], [BIB-IAEA-ADDITIONAL-PROTOCOL].
- WHO IHR Monitoring & Evaluation Framework (capacity review + mutual accountability): see [BIB-WHO-IHR-MEF].
- Audit program guidance (principles, competence, reporting): see [BIB-ISO-19011].

## Kernel anchors (do not repeat)
- Coercion boundary + enforcement event logging: `05-...`, `43-...`.
- Appeals/redress lanes for enforcement decisions: `36-...`, `08-...`.
- Publication integrity for standards and inspection criteria: `53-...`, `27-...`.
- Records custody for evidence and outcomes: `31-...`.
- Person-facing access + contestability for inspection/enforcement outcomes: `98-persons-path-and-accessibility-invariants.md`.
- Protective legibility + adoption dynamics (verification can become dashboard theater): `99-protective-legibility-and-adoption-dynamics.md`.

## Named tensions (design must surface these)
- Deterrence and safety vs cruelty and selective enforcement.
- Inspection rigor vs burden/throughput (don’t create denial-by-process).
- Discretion for context vs rule-bound predictability (and corruption risk).
- Transparency of criteria vs gaming/avoidance.

---
## A) Minimal promise (what “verification” must deliver)
A verification spine MUST make it possible for an independent reviewer to answer:
1) **What was required?** (cite `RULE-*` / `STD-*` / `CMP-*` as‑of)  
2) **What evidence was provided?** (link to `REL-*` and underlying artifacts)  
3) **How was it checked?** (audit/inspection method + sampling + conflict controls)  
4) **What was found and what happened next?** (`DRR-*` → `OFR-*` follow‑through; `AL-*` lanes)  
5) **What changed because of failures?** (corrective actions verified; repeat patterns escalated)

Design rule: verification is **not** only punishment. It is a learning loop that makes obligations **legible, contestable, and correctable**.

---

## B) MVVI components (keep it small)

### B1) Obligation inventory (what is in-scope)
- MUST: each verification program publishes a scope statement + the controlling obligations it checks:
  - instruments: `RULE-*` (law/regulation/permit) and/or `CMP-*` (compact/treaty) and/or `STD-*` (pinned standard versions).
- SHOULD: scope assignment emits `DRR-TYPE: SCOPE` when verification authority crosses jurisdictions (`54-...`).

### B2) Evidence pipeline (what counts as evidence)
- MUST: evidence is published or fileable as `REL-*` with **methods + uncertainty + revision logs** (`51-...`, `26-...`, `53-...`).
- MUST: evidence releases carry join-keys to the obligated entity (`EID`) and the obligation (`RULE-*`/`STD-*`/`CMP-*`).
- SHOULD: where evidence is sensitive, publish a **withholding receipt** (`DRR-*` with review date) and an existence log (`77-...`).

### B3) Audit/inspection program (how checking happens)
- MUST: publish a verification plan (cadence + coverage + sampling logic + independence controls) as a `REL-*` “verification schedule”.
- MUST: investigators/auditors/inspectors have explicit authority and constraints (ledger entry + delegation receipts where applicable) (`34-...`, `78-...`).
- SHOULD: use **risk-based + randomized** elements to reduce gaming and bias; publish the selection method at an appropriate abstraction level.

### B3a) Sampling policy card (portable; anti-gaming)
Verification regimes get gamed when selection is predictable or discretionary. Publish a small **sampling policy** so outsiders can understand coverage, bias risks, and why any given audit was selected.

**Principle:** mix **risk-based** targeting (to focus on harm) with a **random** component (to prevent evasion and bias).

**Anchors:** audit sampling guidance in INTOSAI financial audit practice notes (ISSAI 1530) ([BIB-ISSAI-1530-PN]) and general audit program guidance ([BIB-ISO-19011]).

**Minimum publishable fields** (as a `REL-*` “sampling policy” release):
```yaml
POLICY-ID: REL-VERIF-SAMPLINGPOLICY-____
APPLIES-TO: (ENF | SRV | CON | TRF | CMP | other)
POPULATION: (what records are in-scope; frame definition)
CADENCE: (e.g., monthly; continuous)
METHOD:
  RISK_COMPONENT: (signals used; scoring bands; override rules)
  RANDOM_COMPONENT: (share of sample; RNG method; seed-handling policy)
  STRATA: (if stratified; equity/geo/size strata)
SAMPLE-SIZE: (target n or %; minimum per stratum)
INDEPENDENCE: (who selects; conflict controls; separation from operations)
SELECTION-LOG: (how selections are recorded; anti-tamper pointer)
BIAS-CHECKS: (how disparate selection is tested and corrected)
DISCLOSURE: (what is public vs protected and why)

```

**Design rule:** if the full method can’t be public (gaming risk), publish a **coarser abstraction** plus an integrity commitment (e.g., third-party sealed method + periodic audits of selector behavior).


### B4) Findings + corrective action (what “noncompliance” triggers)
- MUST: material findings emit `DRR-TYPE: INSPECTION` (or `AUDIT`) that cites:
  - controlling obligation(s) (`RULE-*`/`STD-*`/`CMP-*` as‑of),
  - evidence releases (`REL-*`),
  - reason codes (`RC-*`),
  - and the contestation lane(s) (`AL-*`).
- MUST: systemic or high-severity findings open an `OFR-*` case within 24 hours with a public timeline and closure criteria (`55-...`, `32-...`).
- SHOULD: corrective action plans are published as `REL-*` with verification checkpoints.

### B5) Due process + remedy (avoid “inspection as coercion”)
- MUST: parties can challenge findings through a discoverable `AL-*` lane with deadlines and interim protection where needed (`36-...`, `08-...`).
- MUST: any person‑facing notice (inspection result, penalty warning, restriction) is **comprehension‑tested** and includes **no‑wrong‑door navigation** to the right lane (what to submit/by when; assistance availability). Where filing is risky, provide confidential/representative options (`98-persons-path-and-accessibility-invariants.md`, `08-...`, `36-...`).

- MUST: inspections that can impose penalties must separate **fact-finding** from **sanction decision**; sanction decisions emit a distinct `DRR-*` with reasons + lane.

---

## C) Compliance ladder (escalation without arbitrariness)
A compliance system SHOULD pre‑commit to a public ladder that matches the domain’s stakes:

1) **Notice + assistance** (clarify obligation; provide technical help)  
2) **Warning + deadline** (publicly logged; measurable corrective steps)  
3) **Corrective action plan** (`REL-*` plan + verification checkpoints)  
4) **Restriction / penalty** (bounded, reviewable; emit `DRR-*`)  
5) **Suspension / termination / referral** (for persistent or severe noncompliance; open/extend `OFR-*`)

**Rule:** every rung change emits a joinable `DRR-*` and references the ladder rung via a portable `RC-*` code.

---

## D) Failure modes (what to defend against)
- **Paper compliance / metric gaming** → include independent checks + randomized elements; publish revision logs; use multiple measures (`TM-4`, `TM-14`).
- **Inspection harassment / selective enforcement** → publish selection policy; audit inspector behavior; ensure `AL-*` remedies (`TM-12`, `TM-16`).

- **Verification as weapon / registry capture** → minimize sensitive exposure, publish withholding receipts when needed, and ensure independent oversight + safe contestation capacity exist before increasing legibility (`TM-29`, `99-protective-legibility-and-adoption-dynamics.md`, `77-...`, `32-...`).

- **Capture of auditors/inspectors** → conflict controls + rotation; publish integrity receipts; log waivers (`79-...`, `22-...`) (`TM-19`).
- **Secrecy laundering** → withholding receipts + review dates; independent protected access (`77-...`) (`TM-27`).
- **No follow‑through** → mandatory `OFR-*` case tracking for material findings + closure evidence (`TM-23`).

---

## E) Where this plugs into the archive (no new ID families)
- **Evidence:** `REL-*` (methods + revision policy)  
- **Obligations:** `RULE-*`, `STD-*`, `CMP-*`  
- **Findings/decisions:** `DRR-*` (typed) with `RC-*` reasons + `AL-*` lanes  
- **Follow‑through:** `OFR-*` cases/findings  
- **Authority:** Unit IDs + delegation receipts (`34`, `78`)  
- **Sensitive material:** withholding receipts + logs (`77`)  
- **Assurance cases:** inspections/audits become evidence nodes (`73`)
