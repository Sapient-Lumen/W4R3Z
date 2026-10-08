# Taxation & Revenue Integrity (Revenue as Legitimacy Infrastructure)

**Purpose:** make *revenue power* (taxes, fees, fines, levies) legible, bounded, and contestable—so the state cannot extract through confusion, discretion, or hidden incidence.

**Person served:** the payer whose life outcomes depend on correct assessment, accessible appeals, predictable clocks, and protection from arbitrary or retaliatory enforcement.

**Joins:** `118-rulemaking-and-change-control.md` (rule versioning), `110-budget-procurement-integrity.md` (money traceability), `131-compliance-and-sanctions-integrity.md` (sanction ladder), `134-legibility-and-complexity-budgets.md` (complexity budgets), `115-information-integrity-and-record-interfaces.md` (record pointers / disclosure clocks), `127-data-governance-and-privacy-interfaces.md` (purpose-bounding).

---

## Design goals (non-negotiables)

1. **No surprise liability**: assessments must be explainable, receipted, and replayable from stable inputs.
2. **Predictable clocks**: clear deadlines for assessment, payment, refund, and appeal—with breach triggers.
3. **Proportional extraction**: penalties and interest cannot become de facto confiscation; hardship lanes exist.
4. **Anti-retaliation**: contestation and protected disclosure cannot increase enforcement risk absent new facts.
5. **Legibility budget**: complexity is treated as a *policy choice* with measurable costs.

---

## Core primitives

### 1) Tax Rule Registry (TRR-*)
A public registry for revenue rules and parameters, versioned and replayable.

**TRR fields (minimum):**
- `TRR.id`, `TRR.version`, `TRR.effective_from`, `TRR.supersedes`
- tax base definition, rates, thresholds, exemptions/credits
- designated authority + scope (`MC-*`/`SCR-*` join to `132`)
- “who is likely to pay” incidence note (plain-language)
- complexity budget reference (`CB-*`) and service promise (`SP-*`)

**Joins:** `RID-*`/`RCR-*` from `118` for shared change-control.

---

### 2) Assessment Receipt (TAR-*)
When a payer is assessed, they get a receipt that allows *replay*.

**TAR fields (minimum):**
- rule version (`TRR.*`), inputs used (with provenance pointers `RCF-*`)
- computations (stepwise), decision points (discretion flags)
- contest window + method + standing lane
- hardship / payment-plan eligibility link
- reviewer identity class (not necessarily a name), anti-retaliation notice

**Replay test:** an independent auditor can recompute the assessment from `TAR-*` + `TRR-*` without privileged systems.

---

### 3) Payment / Withholding Receipts (TPR-* / TWR-*)
Every payment and withholding event is receipted and joinable.

- `TPR-*`: payment time, amount, channel, allocation (principal/interest/penalty), remaining balance
- `TWR-*`: withholding source, basis, amount, reconciliation schedule

**Failure mode prevented:** “black box withholding” where payers cannot reconcile what was taken and why.

---

### 4) Refund & Reconciliation Receipts (TRF-* / TRC-*)
- `TRF-*`: refund basis, amount, method, due-by date, escalation path if late
- `TRC-*`: reconciliation outcomes (over/under), reason codes, next steps

**Clock:** refunds have hard deadlines; missed deadlines trigger **interim protection** (e.g., interest paid automatically, expedited review) per `105`.

---

### 5) Discretion Boundaries (DDB-*)
Where discretion exists (audits, estimates, settlements), it must be bounded.

**DDB fields:**
- authorized discretion types
- prohibited bases (protected traits; retaliation proxies)
- required documentation (what must appear in `TAR-*` / case file `CFR-*`)
- random-audit integrity hook (`DR-*` from `119`) for sampling fairness

---

## Clocks, triggers, and circuit breakers

- **Assessment clock:** if agency misses statutory assessment deadlines, default outcomes must be explicit (no indefinite open liability).
- **Appeal clock:** if appeal not heard by deadline, trigger interim relief (stay on collection; fee/penalty freeze).
- **Refund clock:** if refund late, trigger automatic interest + escalation + audit flag (`FTL-*` join to `130`).
- **Complexity breach:** if `CB-*` breached (too many steps/docs/cost), trigger required redesign or alternative lane (assisted filing, presumptive eligibility, simplified regime).

---

## Equity without opacity (avoid “fairness theater”)

- **Incidence notes** must be published in plain language for major changes (who likely bears burden; uncertainty acknowledged).
- **Targeting controls:** credits/exemptions that require insider knowledge must be paired with outreach + auto-enrollment where lawful (join to `108` service promises).
- **Hardship lane** must be non-punitive and fast: deferral, installment, or partial forgiveness with receipts.

---

## Minimal publishable metrics (dashboard)

- assessment error rate (over/under), appealed vs. upheld
- median time: assessment → resolution; refund due → paid
- complexity budget: steps/docs/time/cost to comply (PPB-*)
- enforcement disparity checks (protected class proxy-safe analysis; publish method)
- retaliation indicators: enforcement actions following contestation events

---

## Red-team failure modes (what this prevents)

- *“Pay first, explain never”* collection without replayable assessment.
- *Selective enforcement* via discretion without bounded receipts.
- *Complexity capture*: rules that are formally equal but practically inaccessible.
- *Seam resets*: evidence and standing erased when cases transfer (`109/114`).
- *Refund denial-by-delay*: making rightful refunds economically impossible.

---

## References (use existing keys where possible)
- See `91-bibliography-extended.md`: OECD tax administration guidance; IMF fiscal transparency (revenue reporting overlap); and rulemaking/evaluation baselines.
