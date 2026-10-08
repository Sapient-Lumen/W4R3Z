# Legislative Process & Drafting Rails (Make lawmaking legible, inspectable, and reversible)

**Problem:** lawmaking routinely fails as an interface: omnibus bundles hide tradeoffs; amendments land as unreadable deltas; implementation surprises arrive post‑passage; “intent” is unknowable to outsiders.

**Design goal:** treat legislation as a **versioned, testable change** to the rule stack with **public diffs**, **plain‑language explanations**, and **receipted process steps** that connect (a) participation → (b) reasons → (c) text → (d) implementation → (e) remedy.

**Non‑goal:** redesign a whole constitutional order. This memo specifies a **minimum viable lawmaking interface** that can be adopted inside many systems.

---

## A. Core invariants

1) **Diff-first**: every proposed legal change is published as a machine‑diffable, human‑readable delta against the current “as‑of” rulebook. (Join: `39-rulebook-and-instruments-registry.md`, `118-rulemaking-and-change-control.md`.)

2) **Plain-language companion**: every bill has explanatory material that makes it easier for non‑insiders to understand what changes and why (without changing legal meaning). Legislative drafting guidance widely emphasizes clarity as a drafting objective. citeturn0search5turn0search1

3) **Single-subject / anti‑bundling discipline**: material changes are not tied together solely to force passage. When bundling is unavoidable, it is explicit and contestable.

4) **Implementation realism**: a bill is incomplete without a minimal implementation plan and readiness checks (staffing, procurement, data, enforcement, remedy). (Join: `208-change-management-and-release-engineering-for-government.md`, `110-budget-procurement-integrity.md`.)

5) **Contestability survives passage**: the public can trace what was proposed, what changed, who changed it, and how to challenge results once in force.

---

## B. Minimal artifacts (publishable packets)

### 1) Bill Packet (`BPK-*`) — required for introduction
A compact bundle (single URL) that includes:
- **Text** (versioned) + **diff** vs current law (`as‑of` pointer)
- **Plain-language summary** (who is affected, what changes, what stays)
- **Authority & scope note** (why this level of government)
- **Rights & equity impact note** (who bears burden; accessibility/language access implications)
- **Fiscal note** (operating + capital + long-run liability)
- **Implementation note** (systems/processes, procurement changes, hiring/training)
- **Enforcement & compliance note** (how discretion is bounded; escalation ladder)
- **Data/record impact note** (new data collections/sharing corridors; retention; audit trail)
- **Remedy readiness** (where appeals/complaints go; time budgets; interim protections)

### 2) Amendment Receipt (`AMR-*`) — required for material amendments
For each material amendment:
- what changed (diff)
- sponsor + timestamp
- rationale
- expected effect (if known)
- any changes to fiscal/implementation/remedy assumptions

### 3) Deliberation & Response Log (`DRL-*`) — required for public participation
A structured log linking submissions → responses → resulting changes (or reasons for non‑change). OGP’s co‑creation standards emphasize inclusive participation with transparency and accountability across stages. citeturn0search3turn0search7

### 4) Enactment Release Note (`REL-*`) — required at passage
A release note for the law as shipped:
- final diff vs introduced version
- effective dates + transition rules
- “what to do now” guidance for affected people
- known risks + monitoring plan

---

## C. Process rails (minimum sequence)

1) **Pre-introduction scoping**
- publish the problem statement + success metric(s)
- publish options considered + why rejected

2) **Introduction gate**
- no introduction without a complete `BPK-*`

3) **Committee / deliberation stage**
- all hearings/submissions listed in `DRL-*`
- every material change produces an `AMR-*`

4) **Finalization gate**
- no vote without a **final** `BPK-*` including implementation + remedy readiness updates

5) **Post-enactment operationalization**
- publish `REL-*` and link to the rule inventory / “as‑of” state
- schedule ex post review date(s) (join: `207-sunset-review-and-rollback-rails.md`, `216-regulatory-impact-assessment-and-ex-post-review-rails.md`)

---

## D. Anti-patterns (failures to catch)
- **Omnibus laundering**: unrelated provisions smuggled in late.
- **Amendment fog**: last‑minute amendments without diffs/reasons.
- **Implementation cliff**: law passes without operational capacity, producing discretionary chaos.
- **Zombie law**: rules remain on books without evaluation, even after repeated failure signals.

---

## E. Quick checks (link to the test suite)
- Can a person read the **diff** and understand the practical effect?
- Can the public see **who amended what and why**?
- Is there a credible implementation plan (people, money, systems) and a remedy lane?

(See `107-governance-test-suite.md`.)
