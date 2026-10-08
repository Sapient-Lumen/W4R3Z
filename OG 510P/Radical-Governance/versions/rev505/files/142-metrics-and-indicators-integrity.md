# Metrics & Indicators Integrity (MIIP)

**Stack relation:** use `290-evidence-statistics-and-publication-integrity-routing-guide.md` for the canonical route across the evidence / statistics / publication-integrity cluster. This memo is the indicator-governance subsystem for Metric Cards, metric-use receipts, and anti-gaming rails; `03` is the person-facing measurement front door; `214` is the institutional evidence-system anchor; `28` handles program commitments; `190` handles experimentation; `184` handles official statistics; `202` handles evidence commons; `37` / `51` / `53` are narrower claims/publication components.

**Problem:** metrics are *governance instruments*. They decide funding, eligibility, queues, sanctions, and reputations. When a metric becomes a target, it becomes corrupting power (Goodhart/Campbell). Poorly designed indicators create hidden exclusion, gaming, and “compliance theatre”.

**Goal:** make metrics **legible, contestable, and anti-gaming by design**—so measurement supports learning and fairness rather than capture.

---

## Core primitives (receipts + registries)

### 1) Metric Card (`MIC-*`)
A public, versioned card for any metric used in decisions:

- **Name / ID / version**
- **Purpose** (what decision(s) it is allowed to influence)
- **Scope** (who/what it measures; jurisdiction; time window)
- **Operational definition** (exact numerator/denominator; inclusion/exclusion)
- **Data sources** + provenance pointers (joins `127/115`)
- **Known failure modes** (gaming, selection effects, Goodhart pressure)
- **Fairness/impact notes** (who might be harmed; mitigation)
- **Confidence** (data quality, missingness, bias risks)
- **Contest lane** (how to challenge errors / definitions / impacts)

### 2) Metric Change Receipt (`MCR-*`)
When a metric definition changes, issue a receipt that includes:

- old/new `MIC-*` versions + **migration note**
- effective date + **non‑retroactivity default**
- expected distribution shift + “who wins/loses” estimate
- required notice window + appeal window (joins `118/111`)
- backtest / shadow period results (if used for enforcement/eligibility)

### 3) Metric Use Receipt (`MUR-*`)
When a metric materially affects a decision (eligibility, sanction, funding, queue position), the Decision Receipt MUST include:

- the **metric version** used (`MIC-*`)
- the measured value + time window
- any overrides + rationale
- uncertainty/quality flags
- contest pathway (joins `106/115/131/140`)

### 4) Indicator Portfolio Register (`IPR-*`)
A register that groups metrics into a portfolio for a program/agency:

- primary outcome indicators vs process/service indicators
- “red team” indicators (gaming detectors)
- disaggregation requirements (by relevant groups/regions)
- evaluation hooks + sunset/review dates (joins `133/122`)

---

## Integrity requirements (non‑negotiables)

1) **Purpose bounding:** a metric may only influence decisions listed on its `MIC-*`.
2) **No single‑metric rule:** high‑stakes decisions MUST not rely on a single indicator; require a portfolio + human‑review lane with receipts.
3) **Shadow‑mode before enforcement:** major metric changes MUST run in parallel (“shadow”) before becoming binding.
4) **Distribution monitoring:** publish shifts; investigate discontinuities and “threshold cliffs” (joins `140`).
5) **Gaming detection:** include at least one “tamper” indicator per portfolio (e.g., discrepancy checks, audit sampling; joins `130/119`).
6) **Seam safety:** transfers between jurisdictions/providers MUST preserve metric history and versions (joins `109/114`).
7) **Plain language & accessibility:** metric cards and use receipts must be understandable to non‑insiders (joins `134/98`).
8) **Appealable measurement:** any person affected by a metric must be able to contest data errors and definition misfit (joins `08/106`).

---

## Common failure modes and fixes (compact)

- **Threshold cliffs (hard cutoffs):** add smoothing, grace bands, or review lanes; publish cliff impact.
- **Proxy drift:** when process metrics replace outcomes, re‑balance portfolio; add outcome indicators + learning loop.
- **Selection bias:** require denominator integrity checks; publish missingness.
- **Perverse incentives:** add counter‑metrics (e.g., “time to close case” vs “quality of resolution”), and prioritize rights/safety over throughput (joins `108/116`).

---

## Minimal publishable metrics (meta‑metrics)

- % of high‑stakes decisions with a joinable `MUR-*`
- reversal rate due to measurement error vs rule error vs discretion abuse
- discontinuity rate at thresholds (cliff detection)
- audit discrepancy rate (measurement integrity audits)

---

## References (keys)

- [BIB-GOODHART-1975] Goodhart’s Law (targets corrupt measures).
- [BIB-CAMPBELL-1979] Campbell’s Law (corruption pressure under social indicators).
