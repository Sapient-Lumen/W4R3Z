# Fiscal Federalism, Open Budgets & Participation Rails (Money as a governance interface)

**Stack relation:** use `302-fiscal-state-budget-revenue-and-transfers-routing-guide.md` for the canonical route across the fiscal-state / budget / revenue / transfers family. This memo is the budget-openness / participation / fiscal-scrutiny specialization; `18` is the broad intergovernmental-finance front door; `217` is the formula-transfer / equalization specialization; `07` is the broad fiscal-governance front door; `110` handles budget readability and procurement-capture mechanics.

**Aim:** make fiscal power (tax, transfers, spending) **legible, contestable, and joinable** across scopes—so budgets don’t become a capture substrate.

This memo adds rails for:
- cross-scope funding (transfers, mandates, equalization)
- budget openness + public participation (incl. participatory budgeting)
- fiscal rules + independent scrutiny

## 191.1 Why this matters (governance failure pattern)

A common illegitimacy loop:
1) responsibility is assigned to one scope
2) money is held by another scope
3) the gap is filled by opaque transfers, earmarks, and emergency supplements
4) people can’t trace outcomes to accountable decision-makers

Open fiscal practices are a standard countermeasure: transparency + participation + oversight.

## 191.2 Minimal fiscal artifacts (receipts)

### A) Budget legibility bundle
- **BUD‑CARD** — Budget Card (one page)
 - what we spend on, why, who benefits, who decides
 - major changes vs last year (deltas)
 - key risks + uncertainties

- **BUD‑LED** — Budget Ledger (machine‑readable)
 - program lines with stable IDs and join keys
 - links to contracts, grants, outcomes, and audits

- **BUD‑DEL** — Budget Delta Receipt
 - material changes (new program, decommission, reallocation)
 - rationale + evidence pointers

### B) Transfers & mandates across scopes
- **TRN‑AGR** — Transfer Agreement Receipt
 - amount + duration + conditions
 - reporting requirements (minimal and standardized)
 - contingency rules (shortfalls; inflation shocks)

- **MND‑FND** — Mandate Funding Receipt
 - for any “unfunded mandate” claim: who imposed, what it costs, what’s funded, what’s not

- **EQL‑FRM** — Equalization Formula Receipt
 - formula (or policy) that equalizes fiscal capacity across regions
 - periodic review clock + appeal lane

## 191.3 Participatory budgeting (PB) as a legitimacy engine

PB is a **bounded lane** where residents decide how a defined portion of spend is allocated.

Design rules:
- publish the eligible budget slice and constraints upfront (`PB‑SLC`)
- provide proposal support + accessibility (not just voting)
- publish implementation clocks for winning projects (`PB‑IMP`)
- public “non‑implementation” receipts (why; what changed; remediation)

PB is widely documented in municipal practice; Porto Alegre’s 1989 program is frequently cited as an early modern reference point.

## 191.4 Oversight: independent fiscal scrutiny

Budgets fail when forecasting and risk disclosure are politicized. A common rail is **independent fiscal institutions** and disciplined budget governance.

- **IFI‑CHTR** — Independent Fiscal Institution Charter Receipt
 - independence guarantees; access rights; publication rights
 - method versioning + reproducibility

- **FRS‑RPT** — Fiscal Risk Statement Receipt
 - guarantees, contingent liabilities, PPP exposure
 - scenario stress tests + triggers for corrective action

OECD budget governance work emphasizes transparency, medium‑term orientation, risk management, and credible oversight mechanisms.

## 191.5 Anti‑capture gates (money integrity)

- **No dark earmarks:** every material earmark must have a `BUD‑DEL` with sponsor/beneficiary trace.
- **Change‑order discipline:** large in‑year reallocations must produce `BUD‑DEL` + public rationale.
- **Joinability:** each spend line must join to procurement (`OCDS`/contracts), grants, and outcomes.

(See also `179-open-contracting-and-procurement-rails.md` and `110-budget-procurement-integrity.md`.)

## 191.6 Cross-scope accountability (who answers?)

For each program line, define:
- **policy owner** (who sets rules)
- **funding owner** (who pays)
- **delivery owner** (who executes)
- **redress owner** (who must fix harms)

Publish a one‑line **Accountability Join** (`ACJ-*`) per program.

## 191.7 Quick tests

- Can a resident find the **one-page Budget Card** and then drill down to machine-readable lines?
- Can you trace program dollars → contracts/grants → outcomes → audits?
- Are transfers and equalization rules **receipted and appealable**?
- If PB exists, are winning projects reliably implemented with clocked status updates?

## References (external)
- Open Government Partnership — fiscal openness overview + open budgets guidance.
- OECD budgetary governance / budgeting resources (principles, oversight, risk).
- World Bank note on participatory budgeting in Brazil (history and diffusion).
- WRI explainer on participatory budgeting (accessible overview + practice).
