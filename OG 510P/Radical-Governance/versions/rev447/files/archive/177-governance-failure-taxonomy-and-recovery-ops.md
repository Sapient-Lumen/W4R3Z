# Governance Failure Taxonomy & Recovery Ops

**Purpose:** give the archive a compact **failure model**: how governance breaks, how you detect it early, and how you recover without making things worse.

**Person served:** anyone living through institutional failure who needs: *continuity*, *truth*, and *remedy*.

**From-below:** failure is not an abstraction; it is missed services, intimidation, corruption, and harms without recourse. This memo is written for those conditions.

(See also: `04-threat-models.md`, `134-legibility-and-complexity-budgets.md`, `115-information-integrity-and-record-interfaces.md`, `107-governance-test-suite.md`, `155-illicit-finance-and-kleptocracy-defense.md`.)

---

## The five failure families

### F1 — Capture (who benefits is not who is served)

**Definition:** decision pathways systematically advantage insiders (money, party, clan, bureaucracy) over affected people.

**Signals**
- revolving door patterns; hidden procurement; conflict‑of‑interest waivers; donor/lobby access asymmetry  
- selective enforcement; “rules for thee” variance

**Primary countermeasures**
- conflict‑of‑interest discipline + cooling‑off + disclosure receipts (`79-conflict-of-interest-and-revolving-door-discipline.md`)  
- procurement transparency + audit trails (`09`, `115`)  
- illicit finance disruption (`117`)

### F2 — Capability collapse (can’t deliver the floor)

**Definition:** the institution cannot reliably execute core duties (staffing, logistics, infrastructure, response).

**Signals**
- chronic backlogs; “silent delay”; outage patterns; unfilled roles; brittle vendors  
- incident recurrence without learning

**Countermeasures**
- service cards + outage receipts + restoration clocks (`137`)  
- staffing and operational doctrine (`09`)  
- complexity budgets and circuit breakers (`134`)

### F3 — Epistemic failure (can’t tell what’s true)

**Definition:** the system cannot produce trustworthy shared facts for decisions, oversight, or dispute resolution.

**Signals**
- unverifiable records; missing minutes; black‑box models; data drift without notice  
- “policy by rumor”; unexplained variance across similar cases

**Countermeasures**
- information integrity + record interfaces (`115`)  
- algorithmic registers and model change receipts (`06-digital-and-algorithmic-governance.md`, `173`, `128`)  
- independent measurement + auditable sampling frames (`03-metrics-and-evidence.md`)

### F4 — Legitimacy fracture (people stop consenting)

**Definition:** the public stops accepting the institution as a valid binder—even if the institution is technically competent.

**Signals**
- widespread noncompliance; parallel institutions; exit behavior; “shadow courts”  
- violence or intimidation at interfaces; low‑trust rumors dominate

**Countermeasures**
- standing + reasons + remedies (person‑facing floors) (`98`, `107`)  
- procedural justice + transparent enforcement (`05-public-safety-and-coercion.md`)  
- deliberate legitimacy rebuilds (constituent assemblies / review dockets) (`171`)

### F5 — Coordination deadlock (no one can bind the whole)

**Definition:** multiple authorities share the problem; none can coordinate the solution; responsibility ping‑pongs.

**Signals**
- “not our jurisdiction”; inter‑agency blame loops; contradictory orders  
- stalled infrastructure/permits due to cross‑scope vetoes

**Countermeasures**
- explicit compacts, binding coordinators, dispute lanes (`114`)  
- portability + continuity duties for people crossing borders (`109`)  
- scope assignment tests (`54`, `103`)

---

## Recovery ops (what to do after failure)

### 1) Stabilize: continuity first
- appoint an interim accountable lane (single binder) (`114`)  
- publish service clocks + contact points (`137`, `115`)  
- protect whistleblowers and affected persons from retaliation (`98`)

### 2) Diagnose: name the failure family
- classify as F1–F5 (often multiple)  
- publish a minimal “what happened” memo with evidence and uncertainty (`115`, `03`)  
- open an incident learning docket; track recurrence (`134`)

### 3) Contain: prevent repeat harm
- add circuit breakers (pause rules / kill switches / temporary moratoria) (`134`, `196-future-guardianship-and-standing.md`)  
- separate powers: operator vs steward vs inspector (`164`, `137`)  
- tighten disclosure and conflict‑of‑interest rules (`79`, `117`)

### 4) Repair: rebuild capability and legitimacy
- remediation plan with funding + staffing + milestones (`09`)  
- external review + re‑certification tests (`107`)  
- participatory repair: affected groups help define success criteria (`98`)

### 5) Restore: re‑handoff with proof
- re‑handoff only after passing explicit tests and publishing change receipts (`107`, `128`)  
- set a review date; do not treat “return” as permanent without monitoring (`134`)

---

## Failure migration (portable continuity when a scope fails)

When any scope fails F2/F3/F4 severely, authority temporarily migrates upward (or sideways to a trusted steward) until tests are passed.

This avoids “subsidiarity as abandonment.”  
(See `176-ideal-governance-by-scope-synthesis.md`.)

---

## Minimal additions to the test suite

Add these as quick checks:

- **T0.4 — Failure migration:** if a scope cannot meet the capability/rights floor, is there an explicit escalation + continuity + return test?  
- **T4.7 — Capture tripwires:** are conflict‑of‑interest waivers and procurement exceptions publicly visible, reviewable, and statistically monitored?

