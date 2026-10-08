# Policing & Use-of-Force Governance Rails

**Stack relation:** use `292-coercion-custody-and-public-safety-routing-guide.md` for the canonical route across the coercion / custody / public-safety cluster. This memo is the policing specialization; `05` is the canonical coercion and public-safety front door; `116` is the portable coercion protocol; `232` is the custody and corrections specialization; `193` is the non-carceral / restorative neighbor.

**Purpose:** specify a *minimal, implementable* governance architecture for policing that is **hard to abuse**, **easy to audit**, and **compatible with democratic legitimacy**.

This memo treats policing as a **high-coercion public service**: it must be bounded by strict necessity, proportionality, and accountability, with **independent investigation** for serious harm.

## Invariants
1. **Preserve life** as the default operational objective.
2. **Use force only when strictly necessary and proportionate**, with escalating safeguards.
3. **No impunity:** credible independent investigation of serious injury/death.
4. **Receipt-first accountability:** decisions and force are legible after the fact.
5. **Non-police alternatives first** for many “calls for service” (mental health, homelessness, routine traffic).

International baseline principles on necessity/proportionality and restraint in firearms use are expressed in UN standards (e.g., the *Basic Principles on the Use of Force and Firearms* and the *Code of Conduct for Law Enforcement Officials*). See References.

## The stack

### A) Charter & scope boundaries (what police may do)
1. **Authority boundaries**
 - Enumerate police powers and **prohibited actions**.
 - Define when police are *not* the correct responder; require **dispatch routing** to non-police response where available.

2. **Mission definition**
 - “Protect persons and rights” prioritized above “arrest counts” or “order maintenance.”
 - Separate *crime investigation* from *public health / crisis response* where practical.

3. **Minimum rights & access**
 - Clear rights notifications in custody.
 - Access to counsel and medical care in custody.

### B) Policy rails (how police act)
1. **Use-of-force policy must be explicit and ranked**
 - Force continuum framed around **least harmful effective option**.
 - Explicit bans/limits: chokeholds/neck restraints (or strict, published exceptions), prolonged prone restraint, punitive pain compliance.
 - “Critical moments” constraints: firearms discharge, vehicle pursuits, raids, no-knock entries.

2. **De-escalation and time**
 - Policy requires time/distance/cover when feasible; supervisors can authorize “slow it down.”

3. **Duty to intervene + report**
 - Officers must intervene to stop unlawful force and must report it.

4. **Body-worn video + evidence handling**
 - Clear activation rules; strict retention for use-of-force incidents.
 - Tamper-evident evidence chain.

### C) Operational observability (how the public knows it’s working)
1. **Force event receipts** (machine-readable incident record)
 - Incident ID; time/location; reason for contact; force types; duration; injuries; medical response; supervisor review.

2. **Public dashboards**
 - Force rates per contact and per population; disparities; injury/death rates; complaints; sustained findings.

3. **Early-warning system**
 - Flag repeated complaints/force events; mandatory review; retraining or removal pipeline.

4. **Stops/searches and arrests legibility**
 - Capture structured reason codes and outcomes; publish aggregates.

### D) Accountability & remedy (what happens when policing goes wrong)
1. **Independent serious-harm investigation**
 - Death/serious injury triggers **external investigation** by an entity independent of the department.
 - Prosecutorial independence safeguards (see `227-prosecutorial-and-disciplinary-integrity-rails.md`).

2. **Civilian oversight with teeth**
 - Oversight body has access to records; can compel testimony/documents (or can refer to a body that can).
 - Public reporting duties; audit of disciplinary outcomes.

3. **Complaint system (“no wrong door”)**
 - Accessible intake; case receipts; clocked timelines; anti-retaliation.

4. **Remedy ladder**
 - Apology + repair; discipline; decertification; civil liability; criminal prosecution (when warranted).

### E) Workforce & culture (how it stays true)
1. **Selection and training**
 - Training centered on de-escalation, crisis response, legality, and procedural justice.

2. **Promotion & incentives**
 - Promotions tied to safety, complaint outcomes, and community trust—not raw enforcement volume.

3. **Union / contract alignment**
 - Contracts cannot block accountability (e.g., destruction of records, mandatory waiting periods before statements that degrade evidence quality).

## Scope assignment (subsidiarity without impunity)
- **Micro/municipal:** primary service delivery + local transparency dashboards + community oversight.
- **Regional/state:** standards for training/certification, decertification registry, independent investigation capacity.
- **National:** minimum rights baseline, statistical standards, cross-jurisdiction learning, civil-rights enforcement backstop.

Use the **Failure Migration Rule** (see `176-ideal-governance-by-scope-synthesis.md`): if the local scope cannot credibly investigate or restrain harm, authority for serious-harm investigation migrates upward until capability is restored.

## Implementation sequence (tight)
1. Publish **force policy** + bans/limits + duty-to-intervene.
2. Stand up **force event receipts** + dashboards.
3. Establish **independent serious-harm investigation lane**.
4. Deploy **early-warning system** + credible discipline/decertification.
5. Shift response mix: expand non-police crisis response where feasible.

## Tests (add to Governance Test Suite)
- **T-Police-01 (Policy legibility):** force policy is public, ranked, and has explicit bans/limits + duty-to-intervene.
- **T-Police-02 (Receipt-first):** every force event generates a joinable incident record with supervisor review.
- **T-Police-03 (Independent serious-harm lane):** death/serious injury triggers independent investigation with public reporting.
- **T-Police-04 (Early warning):** repeated force/complaints trigger mandatory review and documented interventions.

## References (minimal)
- UN OHCHR: *Basic Principles on the Use of Force and Firearms by Law Enforcement Officials* (1990): https://www.ohchr.org/en/instruments-mechanisms/instruments/basic-principles-use-force-and-firearms-law-enforcement
- UN OHCHR: *Code of Conduct for Law Enforcement Officials* (1979): https://www.ohchr.org/en/instruments-mechanisms/instruments/code-conduct-law-enforcement-officials
- Council of Europe CPT standards (police custody & prevention of ill-treatment): https://www.coe.int/en/web/cpt/standards
- IACP Policy Center (Use of Force resources / consensus model pointer): https://www.theiacp.org/resources/policy-center-resource/use-of-force
