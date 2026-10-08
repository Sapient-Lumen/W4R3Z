# Subsidiarity & Scope Assignment Test (Make “who owns this?” auditable)

**Purpose:** assign responsibilities to the lowest viable scope while preserving rights, remedy, and fiscal accountability.

Subsidiarity is only useful if it can be **applied, documented, and contested**.
This memo defines a compact **Scope Assignment Test** for:
- creating a new authority,
- transferring a mandate,
- changing a boundary,
- delegating power through a compact,
- or shifting enforcement responsibility.

It is the canonical “how” behind `IOP-10` (scope assignment & mandate transfer protocol) and the `DRR-TYPE: SCOPE` record.

**Boundary changes:** pair this test with `92-boundary-change-checklist.md` for implementation gates (records, finance, remedy, elections).

**Anchors:** subsidiarity as “lowest effective level” ([BIB-TEU-A5], [BIB-EURLEX-PROTOCOL2], [BIB-UN-DESA-SUBSIDIARITY-2025]); fiscal federalism (heterogeneity vs spillovers) ([BIB-OATES-1999-FISCALFED]); multi-level reform lessons ([BIB-OECD-MLG-REFORMS-2017]); decentralization design notes ([BIB-WB-DECENTRALIZATION-BRIEFNOTES]); polycentric governance ([BIB-OSTROM-POLYCENTRIC-2010]).

## Kernel anchors (do not repeat)
- **From-below usability:** these artifacts MUST remain comprehensible and actionable via the person’s path (assisted/offline options; no insider knowledge). (`98-persons-path-and-accessibility-invariants.md`)
- Scope ladder + interface obligations: `14-...`, `71-...`.
- Functional authorities and reality mapping: `15-...`, `34-...`.
- Interop join keys (minimal boundary contracts): `70-...`.
- Adoption dynamics / discretion shifts: `99-protective-legibility-and-adoption-dynamics.md`.

## Named tensions (design must surface these)
- Local autonomy vs equal-rights floors (avoid “subsidiarity as abandonment”).
- Fragmentation vs resilience (polycentric strength vs coordination failure).
- Simple tests vs fidelity to complex harm chains.
- Boundary clarity vs flexibility during transition states/crises.

---
## A) The rule (default posture)

**Default:** assign decisions to the **lowest level** that can meet a defined **capacity + rights + integrity floor**.

**Escalate only if** one (or more) of the failure conditions below is demonstrated *with minimal evidence*.

**Key anti-failure constraint:** rights-affecting coercion and eligibility gates always require **effective remedy** and a **justiciable baseline** (see `08-...`, `36-...`, `21-...`).

---

## B) The Scope Assignment Test (seven checks)

Each check records: **Claim → Evidence pointer(s) → Decision**. Keep evidence as joinable pointers (`REL-*`/records), not essays.

### 1) Local knowledge & preference heterogeneity (LK)
**Question:** is performance meaningfully improved by tailoring to local context or preferences?

- **Assign downward** when heterogeneity is high and impacts are contained.
- **Escalate upward** when uniformity is required to protect rights or preserve the common market.

**Minimal evidence:** variation map, user need evidence, service outcome variance (`REL-*`), or credible domain standard.

### 2) Spillovers & externalities (SP)
**Question:** do costs/benefits fall outside the boundary of the decision-maker?

- **Escalate upward** when spillovers are material and persistent.
- **Alternative:** keep local decision but add a **compact** (`CMP-*`) or conditional transfer (`TRF-*`) that internalizes the spillover.

**Minimal evidence:** spillover map/measurement (`REL-*`), cross-unit incident logs (`OFR-*`), or corridor/basin model.

### 3) Scale economies, capex, and fixed-cost absorption (SC)
**Question:** does scale materially reduce cost or increase reliability (network goods, rare expertise, big capex)?

- **Escalate or federate** when scale is decisive.
- Prefer **functional authorities** over full tier inflation (see `15-...`, `16-...`).

**Minimal evidence:** cost curve, capex envelope, reliability model (`REL-*`), audit of duplication.

### 4) Coordination failure / collective action (CF)
**Question:** does fragmented action predictably fail (race-to-the-bottom, under-provision, free riding)?

- **Escalate upward** for credible coordination problems.
- **Alternative:** a compact with enforcement ladder and verification.

**Minimal evidence:** historical failure, credible game/market structure, or measured under-provision (`REL-*`).

### 5) Rights protection & integrity/capture risk (RI)
**Question:** is local control likely to produce rights violations, discriminatory exclusion, or capture?

- **Escalate upward** when rights risk is high or remedy is non-credible.
- **Alternative:** keep delivery local but place **standards + oversight + remedy** at higher scope.

**Minimal evidence:** disparate-impact signals, complaint patterns (`ALR`/`OFRR`), integrity indicators (`INT-*`/`OFR-*`), or credible risk assessment.

### 6) Capacity & enforceability floor (CAP)
**Question:** can the unit actually execute reliably (staffing, systems, procurement, compliance, enforcement constraints)?

- **Assign downward** only if the unit meets a defined minimum capacity floor.
- If not, either: (a) **transfer** the mandate, or (b) **retain** it but attach time-bounded capacity-building conditionality.

**Minimal evidence:** staffing/service metrics (`SRV-*`), audit findings (`OFR-*`), budget execution releases (`REL-*`).

### 7) Exit/voice alignment & responsiveness (EV)
**Question:** do affected people have meaningful voice, contestability, and (where appropriate) exit/portability?

- **Assign downward** when voice is strong, remedies are fast, and “wrong-door” routing is low.
- **Escalate upward** when people are trapped without credible remedy.

**Minimal evidence:** remedy timeliness (`AO-*`), wrong-door rate, participation coverage (`ENG-*`), portability hooks.

**Person’s Path test (ship-blocking):** regardless of scope, the chosen unit MUST be able to meet the `98` person-facing invariants for any high-stakes decision it administers (comprehension-tested receipts, no-wrong-door routing, safe contestation/representation, and non-digital fallback where needed). If it cannot, either (a) move the mandate, or (b) keep delivery local but place **remedy/navigation/oversight** at higher scope with enforceable service standards (`82`).

**Protective legibility check:** if transparency will predictably be weaponized or ignored (no independent enforcement, no organized countervailing power), treat “publish a registry” as insufficient; design for safety + enforceability (`99`).

**Cultural pluralism:** functional equivalents (customary/consensus/restorative) may satisfy the spirit of “voice” and “remedy” even when the implementation is not registry-centric; record the equivalent interface and how contestation works.
---

## C) Decision outputs (what must be produced)

Any scope assignment decision MUST produce:
1) a `DRR-TYPE: SCOPE` record (see `31-...`),
2) a competence-ledger update (old → new version) (`34-...`),
3) money alignment (budget/transfer joins) (`18`, `35`),
4) remedy continuity mapping (`36`),
5) a review trigger (sunset or re-test conditions).

**Important:** many cases are best handled by **splitting the mandate**:
- *Standards + rights baseline* at higher scope,
- *delivery + adaptation* at lower scope,
- *verification + remedy* at an independent forum.

---

## D) Minimal “Scope Test Docket” (attachable to `DRR-TYPE: SCOPE`)

Keep it one screen; store deep evidence as pointers.

```yaml
SCOPE-TEST:
  DEFAULT: lowest_effective_level
  LK: {claim: ..., evidence: [REL-____], result: (PASS|FAIL|PARTIAL)}
  SP: {claim: ..., evidence: [REL-____], result: (PASS|FAIL|PARTIAL)}
  SC: {claim: ..., evidence: [REL-____], result: (PASS|FAIL|PARTIAL)}
  CF: {claim: ..., evidence: [REL-____], result: (PASS|FAIL|PARTIAL)}
  RI: {claim: ..., evidence: [OFR-____, REL-____], result: (PASS|FAIL|PARTIAL)}
  CAP:{claim: ..., evidence: [REL-____, OFR-____], result: (PASS|FAIL|PARTIAL)}
  EV: {claim: ..., evidence: [REL-____, ENG-____], result: (PASS|FAIL|PARTIAL)}
DECISION:
  ASSIGN: (UNIT-____)         # who owns the decision right
  DELIVER: (UNIT-____)        # who delivers (may differ)
  STANDARDIZE: (UNIT-____)    # who sets baseline standards (may differ)
  REVIEW-TRIGGER: (date or condition)
  MONEY: {TRF: [TRF-____], REL: [REL-____]}
  REMEDY: {AL: [AL-____], continuity_plan: ...}
```

---

## E) Re-test triggers (when scope must be reconsidered)

Any assignment MUST name ≥1 trigger. Use measurable signals where possible.

- **Spillover growth:** externality crosses threshold (e.g., corridor/basin indicator).
- **Rights failures:** sustained high-stakes harms, interim protection failures, disparate impact.
- **Capacity collapse:** repeated audit failures, chronic backlog, safety incidents.
- **Capture indicators:** repeated conflicts, procurement anomalies, influence concentration.
- **Technology shift:** changes the scale/cost curve or creates new cross-border effects.

When a trigger fires, issue a new `DRR-TYPE: SCOPE` with the updated docket.

---

## Where this plugs in
- `02-design-toolkit.md` (`IOP-10`)
- `14-scope-ladder.md` (ideal governments by scope)
- `34-competence-ledger-and-mandate-registry.md` (ledger lifecycle)
- `70-interoperability.md` (boundary interfaces)
