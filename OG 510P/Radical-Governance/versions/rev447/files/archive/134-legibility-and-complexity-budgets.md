# Legibility and complexity budgets

Governance fails at the interface when it is *too costly to understand, comply with, or contest*. This memo makes **complexity** an explicit, auditable variable: systems must publish **budgets** for time/steps/cognitive load, and must trigger circuit-breakers when budgets are exceeded.

This is not “UI polish.” It is anti-arbitrariness and anti-capture: complexity is a covert tax that falls hardest on people with least time, money, status, or language access.

Joins: person-facing invariants `98`, protective legibility/adoption `99`, service standards & time budgets `108`, information/record interfaces `115`, rulemaking change control `118`, data/privacy interfaces `127`, interoperability `128`, and audit integrity `130`.

## Primitives

### Complexity Budget (CB-*)
A published *upper bound* on the effort required for a person to:
1) learn what applies, 2) comply, 3) obtain a decision, 4) contest/appeal, and 5) transfer/port.

**CB-Fields (minimum):**
- **CB-APPLIES:** how a person determines applicability (inputs required; lookup method).
- **CB-STEPS:** maximum number of discrete steps (including handoffs) for the “normal” lane.
- **CB-TIME:** max calendar time to completion (ties to `108` time budgets).
- **CB-COST:** fees + typical third-party costs (not “optional”) expressed as a range.
- **CB-DOCS:** maximum number of distinct evidence items; evidence ladder path (ties to `125`).
- **CB-LANG:** minimum language-access set and accessibility modes.
- **CB-FALLBACK:** what happens when budgets are exceeded (see Circuit breakers).

Publish CB-* per *service* and per *lane* (normal, expedited, emergency).

### Person Path Budget (PPB-*)
A CB specialization for the **end-to-end person path** (from need → outcome), spanning multiple agencies/vendors.

- Requires one accountable owner (“one accountable face”) per path.
- Uses continuity defaults from `109/114` to prevent “reset” at seams.

### Plain-Language Requirement (PLR-*)
Any rule, decision, or receipt that binds a person must have:
- a **plain-language summary** (≤ 1 page),
- a **formal version** (canonical), and
- a **diff view** when updated (ties to `118`).

**Receipts join:** PLR must be included in Decision Receipts (`DRR-*` in `106`) and Rule Change Receipts (`RCR-*` in `118`).

### Complexity Incident Ledger (CIL-*)
A public ledger of complexity failures:
- budget breach (CB-TIME/CB-STEPS/CB-COST exceeded),
- language/access breach,
- seam reset breach,
- “impossible proof” loop detected.

Each entry includes: impact, lane, root cause, fix owner, deadline, and whether interim protection was granted.

## Circuit breakers (when budgets are exceeded)
When CB/PPB budgets are breached, systems must trigger one or more:
- **auto-escalation** to a human resolver with authority,
- **interim protection** (status quo / continuity),
- **auto-approval** where risk tier allows (with audit flag),
- **fee waiver** / cost cap,
- **evidence reduction** to the minimal sufficient set,
- **deadline-based default** (ties to `108`, `104`, `130`).

All circuit-breaker activations must produce a receipt and be auditable.

## Metrics (minimum publishable)
- Median and p90 **steps**, **days**, and **out-of-pocket cost** per lane.
- **Drop-off rate** by step and by seam (handoff point).
- **Language/access coverage** (by mode) and request fulfillment time.
- **Contest success rate** and time-to-remedy (ties to `08`, `107`).
- Count and resolution time for **CIL-*** entries.

## Notes and citations
- Plain-language requirements and accessibility are treated as governance obligations rather than optional UX (see `98`, `99`).
- Suggested anchors: [BIB-US-PLAIN-WRITING-ACT], [BIB-OECD-PLAIN-LANGUAGE], [BIB-UK-GDS-CONTENT], [BIB-W3C-WCAG].
