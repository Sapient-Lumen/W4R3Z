# Shared Services & Federated Administration Rails

**Purpose:** enable jurisdictions to share back‑office and delivery capacity (IT, payroll, procurement, casework platforms, call centers, fraud analytics, inspections) **without** creating a shadow state, rights cliffs, or capture-by-vendor.

**Person served:** a person who just wants continuity—same rights, same clocks, same appeal lane—even when the service is delivered by a shared unit or cross‑jurisdiction provider.

**From‑below:** shared services MUST make government *more legible and reliable*, not more opaque.

---

## TL;DR
Shared services are a **polycentric operating model**: multiple accountable principals + one or more shared operators. This memo defines the minimum rails so sharing capacity does not break:

- **accountability** (who is responsible?)
- **portability** (do clocks/evidence reset?)
- **records** (can you obtain the “as‑of” rule + case file?)
- **redress** (is there a no‑wrong‑door appeal lane?)
- **exit** (can a jurisdiction leave without service collapse?)

Anchors: interoperability (`70/128`), scope obligations (`71`), portability (`109`), dispute ladder (`114/195`), procurement integrity (`179/110`), integrity stack (`187`), change/release discipline (`208/51`).

---

## 1) The shared-services model (terms)

- **Principal jurisdictions (PJ):** the elected/constitutional authorities that own policy and remain accountable.
- **Shared Service Operator (SSO):** runs a service component (platform, call center, payment rails, inspection unit) under contract or statutory delegation.
- **Service Component (SC):** a discrete unit of delivery (e.g., eligibility engine, payments, scheduling, hotline).
- **Service Card (`SSC-*`):** public description of the component, obligations, clocks, data flows, and redress lanes.

**Rule:** a shared service MUST be **componentized**. “All of welfare for five regions” is not a component; “payments disbursement rail” is.

---

## 2) Non‑negotiable invariants

1) **No accountability laundering.** A person must be able to identify the accountable authority for an outcome.
2) **No rights cliff at the seam.** Transfers between principals/operators MUST preserve standing, clocks, and evidence (non‑reset).
3) **No silent swaps.** Material changes to shared components must ship as Change Packets + Release Notes and be replayable “as‑of.”
4) **Exit is real.** A principal jurisdiction must be able to exit with bounded disruption using pre‑defined exit artifacts.

---

## 3) Required public artifacts (minimum viable)

### 3.1 Shared Service Card (`SSC-*`) — per component
Publishes:
- component name + owner(s) + operator
- scope of authority (what it can/can’t decide)
- service promises (SLOs) and **time budgets**
- data inputs/outputs with purpose and retention
- what receipts are emitted (Decision Receipts, access/share receipts)
- redress/appeal lane(s) and **no‑wrong‑door routing**
- audit and inspection hooks
- emergency/degraded mode behavior

### 3.2 Shared Services Compact (`SSCMP-*`) — per program family
A compact among principals and the operator that includes:
- governance (board/steering, voting, quorum, conflict rules)
- cost allocation method (with revision discipline)
- dispute ladder and binding decider (`114/195`)
- change management rules (`208`) and versioning obligations
- procurement boundary clauses (anti‑capture, change orders, subcontract disclosure)
- transparency baseline (FOI/ATI equivalence obligations)

### 3.3 Exit Artifact Package (`EXIT-*`)
To prevent hostage dynamics:
- data export schema + frequency
- configuration export + rule versions
- runbooks and dependency list
- escrow for critical docs/keys where needed
- transition SLOs and mutual aid plan

---

## 4) Delegation and authority-chain discipline

Shared operations often blur authority. Apply:

- **Mandate Cards + delegation receipts** (`132/78/141`): the operator’s authority must be explicit and revocable.
- **Decision Receipt joins** (`DRR-*`): each person-impacting outcome must cite the principal jurisdiction and rule version.

**Prohibition:** operators cannot become de facto rulemakers. Parameter changes that affect eligibility, priority, or enforcement intensity are **policy changes**, not “ops,” and require a Change Packet.

---

## 5) Data governance at seams

- **Corridor Registry**: every cross‑entity data-sharing corridor must be enumerated and versioned (`211`).
- **User-visible access ledger** where feasible (`211`).
- **Purpose binding**: principal jurisdictions are responsible for legality of purpose; operators are responsible for access-control and logging (`127`).

**Hard rule:** if the shared service uses analytics to trigger investigations/enforcement, publish the decision pathway and contest lane (joins: `131/140/146/191`).

---

## 6) Procurement and vendor capture defenses

Shared services are high-risk capture surfaces.

Minimum:
- open contracting disclosure baseline (`179`)
- change-order transparency + caps (`179/110`)
- subcontractor disclosure + anti-shell rules
- vendor performance ledger and renewal/sunset discipline (`178/179`)
- independent audit rights + penetration testing rights for critical systems (`130/59`)

---

## 7) Failure modes (and what to do)

### A) Accountability ambiguity
**Signal:** people cannot identify the accountable authority.
**Fix:** enforce `SSC-*` cards + require DRR joins to principal authority.

### B) Seam rights cliffs
**Signal:** transfers reset clocks/evidence; “start over.”
**Fix:** portability kit (`109`), no‑wrong‑door routing (`195`), and continuity duty.

### C) Operator rulemaking by stealth
**Signal:** parameter changes alter eligibility/enforcement without published change.
**Fix:** enforce change/release discipline (`208/51/118`); treat stealth changes as integrity incidents.

### D) Hostage exit
**Signal:** jurisdictions cannot leave without service collapse.
**Fix:** require `EXIT-*` package at contract start; escrow; staged exit drills.

---

## 8) Metrics (publishable)

- time‑to‑first meaningful response (by lane)
- transfer success rate without clock reset
- number of “seam incidents” per quarter (missing receipt, wrong-lane routing, silent change)
- change-order ratio (% of contract value)
- renewal outcomes (renew/reshape/sunset) and reasons

---

## 9) Minimal tests (for `107-governance-test-suite.md`)

- shared services have `SSC-*` + `SSCMP-*` + `EXIT-*`
- DRR joins identify principal authority and rule version
- change packets exist for material component changes
- portability invariants hold across the seam
