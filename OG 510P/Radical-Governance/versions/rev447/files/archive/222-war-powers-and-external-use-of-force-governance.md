# 222 — War powers and external use-of-force governance

**Purpose:** make the highest-coercion decisions (external use of force, armed conflict participation, security assistance that predictably enables abuse) **legible, contestable, time‑bounded, and auditably constrained**.

This memo treats war powers as an *exercise of authority* that MUST emit durable, joinable artifacts—without forcing operational disclosure.

**Joins:** `05-public-safety-and-coercion.md`, `23-emergency-governance-and-exceptions.md`, `77-sensitive-information-and-secrecy-governance.md`, `106-legitimacy-protocols.md`, `112-exception-control-and-emergency-powers.md`, `131-compliance-and-sanctions-integrity.md`, `156-judicial-systems-and-constitutional-review.md`, `168-intelligence-and-secrecy-governance.md`, `231-supreme-audit-institutions-and-public-accounts-rails.md`.

**External references:** UN Charter on force and collective security **[BIB-UN-CHARTER]**; ICCPR derogations and notice duties **[BIB-ICCPR]**; basic use‑of‑force principles (domestic context, for analogy of proportionality + accountability) **[BIB-UN-UOF]**.

---

## A. Scope and classification

This memo covers:

- **Use-of-force authorizations** (air strikes, raids, cyber operations with kinetic effects, support that is functionally co-belligerency).
- **Security assistance** (training, weapons transfers, intelligence sharing) when there is a credible risk of misuse.
- **Exceptional secrecy claims** that would otherwise defeat accountability.

**Not covered:** detailed operational doctrine.

---

## B. The non-negotiable floors

1) **Civilian supremacy + lawful basis:** authority must cite a clear constitutional/statutory basis *and* the international-law frame being asserted.

2) **Time bounds + renewal discipline:** no open‑ended authorizations.

3) **Independent oversight with access:** an oversight body must be able to inspect classified annexes and publish non-sensitive outcome summaries.

4) **Contestability without disclosure:** courts/independent reviewers can review in camera where needed; public gets a reasons summary plus a challenge lane.

5) **Harm accounting:** civilian harm and foreseeable misuse must be measured and acted on.

---

## C. Minimal artifacts (don’t invent more than needed)

### 1) `WPR-*` — War Powers Receipt (authorization docket)
A `WPR` is issued for every use-of-force episode and every continuing authorization.

**Public fields (MUST):**
- `WPR-ID`, issuing authority, date/time, expiry/review-by date
- scope: geography, actors, operation class (broad), assistance types
- legal basis pointers: `RULE-*` / constitutional clause pointer / treaty pointer
- **objective statement** (one paragraph)
- **necessity & alternatives** summary (why non-force options are insufficient)
- **proportionality & reversibility check** (`PRC-*` style, short)
- constraints: targeting constraints at a non-technical level (protected sites, no-strike categories), detention/capture constraints
- oversight access pointer (which committee/inspector has access) + how public can file complaints

**Classified annex (MAY):** sources/methods, targeting intelligence, partner identities, operational plans.

### 2) `WUR-*` — War Use Review (renewal / termination)
Issued on renewal, material scope change, or termination.

Includes:
- what changed, why, and what evidence moved the decision
- compliance summary (violations, near-misses)
- harm summary (see `COH-*`)
- a sunset / exit plan (how the authorization ends)

### 3) `COH-*` — Civilian Outcome & Harm Record
A standardized record of:
- civilian harm allegations + status (credible/unclear/not credible)
- methodology note (what was checked; what cannot be checked)
- remediation actions (apology, compensation, policy change)

**Privacy note:** publish aggregates by default; person-level data is protected with disclosure lanes for affected parties.

---

## D. Approval gates (minimum viable constraints)

### Gate 0 — Legitimacy classification
Classify the decision:
- **DEF-1:** immediate defense of territory/people (imminent threat)
- **DEF-2:** collective defense / treaty obligations
- **SEC-1:** security assistance (non-kinetic) with misuse risk
- **FOR-1:** discretionary external force (highest scrutiny)

Scrutiny increases by class; `FOR-1` requires the strongest renewal discipline.

### Gate 1 — Evidence & alternatives pack
Before `WPR` issuance, an evidence pack MUST exist (even if classified) and be summarized publicly as `REL-*`:
- threat assessment and confidence levels
- civilian harm risk assessment
- alternative options considered
- exit conditions / off-ramps

### Gate 2 — Dual-key authorization
For any authorization beyond immediate self-defense:
- **executive proposes**, **legislature authorizes** with time bounds
- renewals require a fresh `WUR` and a recorded vote or equivalent public action

### Gate 3 — Oversight access guarantee
A named independent oversight body has:
- access to classified annexes
- subpoena/compulsion power where relevant
- duty to publish periodic non-sensitive findings

---

## E. Secrecy discipline (so secrecy can’t be used to defeat remedy)

- Treat withholding/classification as a **decision**: issue a withholding receipt and a review-by date (`77`, `168`).
- **No secrecy without expiry:** classification must carry a time-bound review.
- **Foreign liaison constraint-evasion controls:** if partners impose secrecy, the domestic oversight body must still be able to inspect; otherwise assistance is suspended (see `168`).

---

## F. Security assistance: “do not enable abuse” rule

Where arms, training, data, or intelligence is shared:

- Require a risk assessment and a **misuse tripwire plan**.
- Publish a minimal assistance docket linked to `WPR` when assistance is operationally intertwined.
- If credible misuse occurs, issue an immediate `WUR` update: pause, restrict, or terminate assistance; publish a non-sensitive summary.

---

## G. Failure modes and tripwires

**Failure mode:** permanent war by authorization creep.
- **Tripwire:** renewals happen without public `WUR` and recorded vote.

**Failure mode:** secrecy shields illegality.
- **Tripwire:** oversight body denied access; classification has no expiry.

**Failure mode:** harm denial.
- **Tripwire:** civilian harm allegations rise but `COH` updates lag; remediation rate collapses.

**Failure mode:** partner laundering.
- **Tripwire:** assistance continues despite repeated partner abuse findings.

---

## H. Minimal test hooks

- Any `WPR` exists → it MUST have an expiry/review-by date and renewal path.
- Any secrecy claim exists → it MUST have a withholding receipt + review-by.
- Any harm allegation exists → it MUST have a `COH` status and remediation pathway.
