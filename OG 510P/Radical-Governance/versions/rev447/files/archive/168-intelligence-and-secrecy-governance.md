# Intelligence and secrecy governance

**Purpose:** prevent "national security" institutions (intelligence, surveillance, classified programs) from becoming a **parallel, unaccountable state**. The design goal is a regime where secrecy is *bounded*, *reviewable*, and *replayable*: you can later trace what authority existed, who approved it, what rules were in force, what safeguards applied, and what remedies existed—without requiring public disclosure of sensitive operational details.

**Scope:** domestic/foreign intelligence services; signals intelligence; counterintelligence; fusion centers; classified procurement/programs; covert action authorities; and the classification/declassification system itself.

**Core failure mode:** secrecy + fear + deference → **unchecked discretion** (rights violations, partisan targeting, corruption, mission creep), plus fragile legitimacy (trust collapses when abuses surface).

---

## Threat model

1) **Parallel power:** secret rules, secret budgets, secret tribunals.
2) **Mission creep:** exceptional tools become routine; "temporary" becomes permanent.
3) **Political abuse:** surveillance and covert powers used against opposition, journalists, minorities.
4) **Secrecy laundering:** abusive programs hidden behind classification; oversight bodies captured or starved.
5) **Vendor/state capture:** proprietary systems + classified contracting block audit and accountability.
6) **Foreign liaison bypass:** "partner" collection used to evade domestic legal constraints.

**Design stance:** treat security/intelligence as a *high‑risk governance domain* requiring stronger-than-normal receipts, independent review, and time-bounded authority.

---

## Invariants

### S-1: Secrecy is a **governance decision** (not an annotation)
Classification must be an explicit, reviewable act with **scope, rationale, and expiry**, not an indefinite label.

**Minimum:** a **Classification Decision Receipt** `CDR-*` capturing:
- the information category and harm rationale
- responsible officer and authority basis
- **expiry date** + review schedule
- redaction plan / partial disclosure path
- appeal / challenge route

(Align with the principle that restrictions on access to information must be necessary and proportionate under law, and that national-security secrecy should be narrowly defined and reviewable. See [BIB-UNHRC-GC34-2011]; [BIB-TSHWANE-2013].)

### S-2: Oversight bodies must have **access + teeth**
Oversight without access to classified information, staff capacity, or the ability to compel documents is theater.

**Minimum oversight set:**
- **Parliamentary/legislative committee** with vetted staff and full access (with sanctions for obstruction)
- **Independent inspector general / audit** for program legality and performance
- **Independent judicial authorization** for intrusive collection (warrants) + adversarial safeguards where feasible
- **Complaint/remedy lane** accessible to affected persons (including where they suspect surveillance)

Comparative baselines emphasize access to classified information and strong mandates for oversight bodies. See [BIB-COE-NS-OVERSIGHT-2015]; [BIB-VENICE-SECURITY-2007]; [BIB-VENICE-SIGINT-2015].

### S-3: Intrusive powers require **pre-authorization + logs**
For surveillance/search/collection powers that affect rights, require:
- explicit legal basis + public rule inventory entry (`25-...`)
- judicial/independent authorization
- bounded duration + renewal thresholds
- tamper‑evident event logs and ex post review

### S-4: Budget secrecy is bounded
Even when line items are classified, the system must prevent "black budgets" from becoming untraceable.

**Minimum:**
- classified budget to oversight committee + national audit institution
- program-level **spend envelopes** and procurement artifacts joinable under controlled access (`CON-*` / `BUD-*` joins)
- limits on off‑book vehicles; treat SPVs as functional authorities (`15-functional-authorities.md`)

### S-5: Disclosure is a *default trajectory*
Secrecy should degrade over time unless ongoing harm is demonstrated.

**Minimum:**
- automatic declassification clock unless renewed with a new `CDR-*`
- periodic public transparency reports (aggregate counts of warrants, selectors, compliance findings)
- protected disclosure channels for whistleblowers (`121-whistleblowing-and-protected-disclosure.md`) aligned with security-sector realities

---

## Minimal viable system (MVS) for intelligence governance

### 1) Public rule inventory + versioning
- All **authorities and methods classes** must appear in the public rule inventory (`25-...`) at least at the level of *legal powers, purposes, guardrails, and oversight*.
- Rule changes are versioned and receipted (`118-rulemaking-and-change-control.md`).

### 2) Authorization dockets for intrusive activity
Create a **Surveillance Authorization Docket** `SAD-*` (not fully public; publishable skeleton metadata):
- authority basis (`RID-*`), purpose code, covered population class
- approval chain (judge/independent authorizer)
- duration, renewal history
- minimization/purpose-bounding controls (joins `127-data-governance-and-privacy-interfaces.md`)

### 3) Program registry and audit hooks
Maintain a controlled-access **Classified Program Registry** `CPR-*`:
- program purpose, responsible office, oversight contacts
- procurement surface (vendors, contracts, change orders) with join keys
- audit plan + findings (joins to `130-audit-and-inspection-integrity.md`)

### 4) Foreign liaison controls
- A **liaison register** (classified) recording partner agencies, data sharing terms, and domestic-constraint compliance checks.
- Prohibit "constraint evasion" via partner collection; require explicit review when foreign data is used domestically.

### 5) Remedy without revealing secrets
Provide "**challengeability**" without full disclosure:
- secure complaint channels (ombuds/IG)
- special advocates / amicus mechanisms in sensitive proceedings where feasible
- ex post notice to targets when risks drop below threshold (consistent with rights and proportionality principles; see [BIB-TSHWANE-2013])

---

## Design patterns

### Pattern A: Classification as change control
Treat classification like a rule change: it has **diffs, expiry, and appeal**. Operational secrets can remain secret, but the *fact of secrecy*, category, and clock are recorded.

### Pattern B: Oversight independence budgets
Oversight bodies require protected budgets and hiring autonomy (`ACC-6`). Starving oversight is a governance failure indicator.

### Pattern C: "Secrecy laundering" detector
Use **red flags**:
- repeated renewals with no narrowing
- recurring "urgent" authorizations
- vendor lock-in + proprietary audit barriers
- large classified amendment/change-order shares (`CON` metrics)

### Pattern D: Emergency lanes are not permanent lanes
Emergency authorizations must follow the emergency-derogation discipline (`112`, `23`) with hard sunsets, published rationales, and ex post review.

---

## Metrics (Goodhart-resistant)

- **Expiry compliance:** % of `CDR-*` reviewed/expired on time.
- **Renewal intensity:** renewal count distribution by authority class (watch fat tails).
- **Oversight throughput:** audits completed vs planned; findings closed vs open aging.
- **Transparency cadence:** on-time publication of aggregate reports.
- **Constraint-evader signals:** instances where foreign liaison data is used domestically without explicit review.

---

## Implementation notes

- Start with **skeleton metadata** that is publishable without operational risk (IDs, clocks, oversight contacts, aggregate counts).
- Create a **sealed audit trail**: public can verify that *an authorization existed and expired* even if details remain classified.
- Make **oversight joinable**: procurement, budgets, audit findings, and rule versions must connect under controlled access.

---

## Pointers

- Coercion ceiling and emergency constraints: `05-public-safety-and-coercion.md`, `23-emergency-governance-and-exceptions.md`, `112-exception-control-and-emergency-powers.md`.
- Privacy/purpose-bounding: `127-data-governance-and-privacy-interfaces.md`, `127-data-governance-and-privacy-interfaces.md`.
- Records and publication integrity: `53-publication-integrity-and-tamper-evident-logs.md`, `115-information-integrity-and-record-interfaces.md`.

**Key references:** [BIB-TSHWANE-2013]; [BIB-UNHRC-GC34-2011]; [BIB-COE-NS-OVERSIGHT-2015]; [BIB-VENICE-SECURITY-2007]; [BIB-VENICE-SIGINT-2015].
