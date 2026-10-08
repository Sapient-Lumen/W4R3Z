# Institutional Circuit Breakers (Anti-Capture + Anti-Runaway Defaults)

**Purpose:** define a small set of **automatic brakes** that trigger when power drifts, corruption rises, or emergencies become pretexts—so correction doesn’t depend on heroics.

**From-below thesis:** when stakes are high, discretionary “good judgment” is not a safeguard. People need **pre-committed triggers** that force pause, review, and transparency.

(See: threat models `04-threat-models.md`; integrity/procurement `22-public-integrity-and-procurement.md`; emergency powers `23-emergency-governance-and-exceptions.md` + rails `165-emergency-powers-derogation-sunsets-rails.md`; oversight `32-oversight-institutions-and-follow-through.md`; fiscal levers `07-fiscal-and-budgetary-governance.md`; remedy `08-remedy-and-grievance.md`.)

---

## A. Circuit-breaker types (small set)

1) **Pause-and-review**  
   Automatic temporary halt of a policy, system, or practice when trigger conditions are met.

2) **Auto-disclosure**  
   Mandatory publication of specific artifacts (contracts, model versions, incident logs, legal basis) when a threshold is crossed.

3) **Auto-escalation**  
   Mandatory handoff to an independent forum (ombuds, inspector general, court, external audit) when internal handling is conflicted.

4) **Auto-compensation / interim protection**  
   Temporary relief while facts are contested where delay or error risks irreparable harm.

5) **Auto-sunset / reauthorization**  
   Powers or programs lapse unless renewed under heightened scrutiny.

---

## B. Standard triggers (portable across scopes)

Use **few, legible triggers**; publish them in plain language.

### 1) Harm / rights triggers
- A spike in adverse outcomes beyond a published band (denials, removals, coercive incidents).
- Credible allegations of rights violations with corroborating indicators (complaints + independent signals).
- A single “red event” class (death in custody, mass outage of benefits, unlawful surveillance finding).

**Default breaker:** pause-and-review + auto-disclosure + interim protection.

### 2) Integrity / capture triggers
- Single-source contracting beyond a threshold; repeated awards to the same vendor; revolving-door conflicts (`22`, `38`).
- Material unexplained variance between unit costs and benchmarks (`07`).
- Patterned whistleblower reports with retaliation indicators.

**Default breaker:** auto-escalation to independent audit + procurement freeze on the affected stream.

### 3) Emergency-power creep triggers
- Emergency rules renewed beyond N days without legislature/jury/citizen panel signoff.
- Exception carve-outs that expand scope or target class beyond the original justification (`23`).

**Default breaker:** auto-sunset + mandatory reauthorization with published evidence + external review.

### 4) Algorithmic governance triggers
- Model/system version change without registry update or without comparable performance evidence (`42`).
- Disparate error rates crossing a published threshold.
- “Black box” refusal to provide decision basis.

**Default breaker:** revert-to-safe version or manual pathway + auto-disclosure + independent technical audit.

---

## C. Minimal breaker kit (what to write into law/charter)

- A **trigger table** (conditions → breaker actions → who executes → by-when deadlines).
- A **public log** of breaker activations (counts, rationale, corrective action).
- A **non-retaliation enforcement clause** (penalties, remedies).
- A **budget link** (funding holdbacks for non-compliance; funding for remedy capacity).
- A **fallback service lane** (manual/analog process during pauses).

---

## D. Design warning (keep it governable)

Circuit breakers fail when they are:
- **Too many** (nobody remembers them) → keep to a small table.
- **Too discretionary** (“may”) → use “must” with narrow exceptions.
- **Unpublished** → trigger table and activations must be public by default.
- **Unenforced** → link to funding + enforceable remedy.

