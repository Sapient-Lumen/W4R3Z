# Coercion Governance: Use of Force and Detention

**Purpose:** Make coercive power (force, arrest/detention, searches, surveillance-like stops) legible, bounded, and contestable — with real brakes.

**Person served:** People subject to coercion; officers/staff who need clear constraints and protection from unlawful orders.

**Principle:** Coercion is where governance fails fastest. Treat it as a *high-risk interface* with mandatory receipts, independent review, and emergency-safe degraded modes.

---

## Minimal protocol (portable across scopes)

### 1) Authorization surface: *clear legal hooks*
- Every coercive action type MUST have a published **Authority hook** (legal basis + scope + non‑delegables) and a plain‑language **material floor** for lawful use.
- If the legal hook changes, publish a **Change Receipt** (see `115-information-integrity-and-record-interfaces.md`).

### 2) Use-of-force ladder + mandatory reporting
- Maintain a published **force continuum** (policy + training + permitted tools).
- Every reportable force event MUST generate a **Force Event Receipt (`FER-*`)** with:
  - time/place; actor unit (not necessarily individual name in sensitive cases);
  - type/level of force; stated justification;
  - injuries/medical aid; witnesses/evidence pointers;
  - immediate supervisor review outcome;
  - independent-review routing (see below).

### 3) Detention receipt (`DER-*`) for any liberty restriction
Any arrest/detention/hold MUST generate a **Detention Event Receipt** delivered to the person (and logged) that states:
- the reason and legal basis;
- rights + counsel/assistance path;
- maximum time bounds + next review time;
- how to contest; how to report mistreatment safely.

### 4) Independent serious-incident pathway (mandatory)
- Force causing **death/serious injury**, credible torture/ill‑treatment allegations, or detention deaths MUST route to an **independent** channel with:
  - immediate evidence preservation;
  - separation from chain-of-command investigation;
  - public reporting with privacy‑safe redactions.

### 5) De-escalation and “mercy while contesting”
- The system MUST define **least-harm defaults** while facts are contested:
  - medical evaluation/aid is automatic;
  - access to counsel/assistance is automatic;
  - interim restrictions on repeat exposure to the same officers/unit where credible complaints exist.

### 6) Anti-retaliation and safe reporting
- Provide a **degraded/offline** safe reporting channel (no personal device required) for complaints and witnesses.
- Retaliation triggers automatic escalation and protective measures (see `83-whistleblowing-and-protected-disclosures.md`).

---

## Circuit breakers for coercion

Trigger **pause / external review / interim constraints** when any of the following occurs (see `105-institutional-circuit-breakers.md`):
- spike in serious incidents or repeat patterns;
- missing evidence pointers (bodycam/officer logs) beyond narrow exceptions;
- repeated time‑bound violations (holds beyond limit);
- substantiated retaliation/chilling signals.

---

## Minimal metrics (publish privacy-safely)

- Rate of force events by category; injury/medical aid rates.
- Time-to-independent-review for serious incidents.
- Detention time distribution vs legal limits; over‑limit count.
- Evidence completeness rate (FER/DER fields present; chain-of-custody intact).
- Complaint resolution time + remedy types; retaliation signals.

---

## Bibliography anchors (see `91-bibliography-extended.md`)

- **[BIB-UN-BPUFF]** Basic Principles on the Use of Force and Firearms (1990).
- **[BIB-UNODC-UOF-RB]** UNODC Resource Book on use of force.
- **[BIB-MANDELA-RULES]** UN Standard Minimum Rules for the Treatment of Prisoners.
- **[BIB-ICCPR]**, **[BIB-HRC-GC29]**, **[BIB-SIRACUSA]** for rights constraints and derogations.

