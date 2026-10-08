# Risk & Safety Assurance Governance (Safety cases that bind)

**Purpose:** treat “risk management” as an **interface** with receipts, clocks, and contestability—so high‑hazard systems (infrastructure, health, transport, AI, finance) cannot rely on informal assurance or opaque expertise.

**Person served:** the person exposed to risk (worker, resident, passenger, patient) who needs **legible guarantees** and a way to force review when safety drifts.

**From-below:** if safety is “handled internally,” it becomes capture‑prone. This memo makes *assurance* a public‑facing lane with minimal publishable artifacts.

---

## Core objects (portable, minimal)

### 1) Safety Case Card (`SCC-*`) — what exists, who owns it, what can go wrong
A one‑page public card per high‑hazard system / program:
- system boundary + dependencies (joins: `128` interface cards; `137` service cards; `138` project cards)
- hazards + top harms (who is harmed, how, how soon)
- safeguards (technical, procedural, organizational) mapped to hazards
- **assurance owner** (named accountable role) + independent reviewer
- monitoring signals + thresholds + what happens when breached (joins: `104/105` control loops + circuit breakers)
- last revision + next review date (joins: `118` change control)

### 2) Safety Assurance Case Receipt (`SACR-*`) — why it is safe *enough* to operate now
Issued at required gates (go‑live, major change, after serious incident, periodic renewal):
- claim(s): what “safe enough” means in measurable terms
- evidence pack pointers (no dumps; stable references, joins: `115`)
- dissent/minority report pointer (if any)
- constraints/conditions (load limits, staffing, maintenance, operating envelope)
- review window + contest lane (joins: `106/08`)
- expiry (no perpetual safety cases)

### 3) Risk Register Entries (`RRE-*`) — the living list of known risks
- risk description + harm + exposure population
- current controls + residual risk statement
- owner + mitigation plan + due dates (joins: `108` time budgets)
- triggers for escalation / pause (joins: `105` circuit breakers)
- link to incidents and changes (joins: `118/130/133`)

### 4) Incident Report Receipt (`IRR-*`) — when the world proves the model wrong
Any serious incident (or near miss over threshold) generates:
- timestamp + affected scope + immediate protective steps
- *what is known / unknown* and data retention commitments (joins: `115/127`)
- independent pathway invoked? (joins: `130` audit/inspection; `116` if coercion involved)
- required follow‑through items with clocks (joins: `130` follow‑through ledger; `133` evaluation loop)

### 5) Waiver / variance receipts for safety (`SVR-*`) — “temporary exceptions” that cannot hide
Any safety waiver must be:
- time‑bounded + publicly logged (joins: `112` exception control style)
- paired with compensating controls
- auto‑escalated when repeated (capture smell test)

---

## Hard rules (non‑negotiables)

1) **No silent operation outside the envelope.** If conditions are violated, trigger pause / degrade‑mode / interim protection and issue an `IRR-*`.  
2) **Change = re‑assure.** Material changes require a new `SACR-*` (joins: `118` rulemaking/change control; `138` change receipts for projects).  
3) **No “acting safety owner forever.”** Assurance ownership follows `113` appointments/tenure integrity; conflicts follow `120`.  
4) **Safety is contestable.** Affected people can trigger review (standing rules in `106`) and file collective patterns (`123`).  
5) **Evidence pointers, not PDFs.** Use stable pointers and disclosure clocks (`115`).  

---

## Minimal publishable metrics (few, hard to game)
- time since last `SACR-*` renewal; % systems past expiry
- rate of serious incidents and near misses (per exposure)
- % follow‑through items closed on time (joins `130/133`)
- # repeated waivers (`SVR-*`) per system (capture smell)
- complexity budget for the safety lane (joins `134`)

---

## Where this plugs in
- **Utilities/critical infrastructure:** `137` + `105` + `130` (outages + inspections + follow‑through).  
- **Capital projects/major IT:** `138` stage‑gates require `SACR-*` at commissioning + after major change.  
- **Coercion / detention:** `116` uses incident receipts; severe events must trigger independent review.  
- **Data/ADS:** `127/115` require purpose‑bounded evidence and auditability for risk claims.

---

## References (anchors)
- Risk management standard: [BIB-ISO-31000].  
- Functional safety / safety lifecycle: [BIB-IEC-61508].  
- Occupational H&S management system: [BIB-ISO-45001].  
- Safety‑case regimes (process hazard / major accidents): [BIB-UK-HSE-SAFETYCASE].  
