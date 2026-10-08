# Threat Models (Cross-Scope Failure Modes)

This memo is a compact checklist of how governance systems break, with mitigation hooks into `02-design-toolkit.md`.

## 1) Capture (by money, parties, factions, or clans)
**Signals:** concentrated donors/vendors; revolving door spikes; policy favors narrow interests; watchdog budget starvation.  
**Mitigations:** `ACC-1/2/4/5`, `OPEN-1/2`, `DEC-2`, transparent appointments, randomized audits.

## 2) Corruption & fraud (procurement and transfers)
**Signals:** single-bid contracts; repeated “emergency” contracting; missing deliverables; weak close-out audits.  
**Mitigations:** `OPEN-2`, `ACC-1/2`, vendor performance histories, hard documentation rules for exceptions.

## 3) Coercion drift (security institutions become political tools)
**Signals:** opaque use-of-force, selective enforcement, intimidation of opposition, impunity.  
**Mitigations:** `SAFE-1/2/4/5`, `LAW-2/3`, public reporting, independent serious-incident investigations, separation of operational command; see `05-public-safety-and-coercion.md`.

## 4) Epistemic failure (decision-makers lose contact with reality)
**Signals:** suppressed stats; politicized public health/environment data; rapid narrative swings; policy without evaluation; information disorder overwhelms institutions.  
**Mitigations:** `OPEN-4/5`, `03-metrics-and-evidence.md` loops, red-team reviews, duty-to-respond, platform/accountability alignment where relevant (Global Digital Compact: https://www.un.org/digital-emerging-technologies/global-digital-compact).

## 5) Legitimacy collapse (participation feels pointless)
**Signals:** low turnout + high cynicism; protests substitute for institutions; minorities excluded; decisions reverse without explanation.  
**Mitigations:** `DEC-2/3`, predictable review cycles, accessible remedy (`ACC-3`, `LAW-3`), rights protections.

## 6) Administrative overload (complexity > capacity)
**Signals:** backlogs; rule explosion; inconsistent decisions; shadow discretion; burnout and turnover.  
**Mitigations:** simplify mandates; publish service standards; build `CAP-1/2`; use tribunals (`LAW-3`); sunset low-value rules.

## 7) Digital/vendor capture (opaque systems govern the public)
**Signals:** proprietary lock-in; un-auditable automated decisions; surveillance creep; data breaches; “terms of service” replacing law; outages-as-denial-of-service.  
**Mitigations:** `IOP-4/5`, procurement transparency (`OPEN-2`), privacy-by-design, audit logs + system registers, independent testing rights, exit clauses.

## 8) Boundary failure (jurisdictional gaps and blame shifting)
**Signals:** “not my job”; unfunded mandates; inconsistent standards; crisis coordination failures.  
**Mitigations:** `70-interoperability.md` interfaces, `IOP-1` compacts, formula-based transfers, clear escalation ladders.



## 9) Ecological overshoot (commons collapse and irreversible harms)
**Signals:** degrading baselines; permit systems divorced from outcomes; leakage across borders; “paper parks”; slow harms with no accountability.  
**Mitigations:** ecological budgets + registries + cross-boundary compacts (`OPEN-6`; `70-interoperability.md`); environmental rule-of-law disciplines; see `11-commons-and-ecological-governance.md`.

## 10) Fiscal illusion (commitments exceed reality)
**Signals:** off-budget vehicles; rising contingent liabilities; repeated “one-off” measures; missing tax expenditure disclosure; optimistic forecasts.  
**Mitigations:** `CAP-2/3/4`, consolidated accounts + audit, fiscal risk statements; see `07-fiscal-and-budgetary-governance.md`.


## Minimal practice
Every scope memo SHOULD include:
- its top 3 threats from this list
- the *one* institutional change that most reduces each threat (small, not heroic)

## 11) Exclusion & invisibility (people fall outside registries)
**Signals:** high unregistered births/deaths; people unable to obtain ID; “paper-only” services; high denial/deferral rates for status; informal payments for documents.  
**Mitigations:** `IOP-6` identity + CRVS baseline with non-exclusion design; accessible enrollment; correction and remedy (`LAW-5`); audit disparities and reduce documentation burdens. See `12-identity-and-recognition.md`.

## 12) Regulatory capture & monopoly rents (utilities and markets)
**Signals:** opaque tariffs/fees; discretionary licensing; exemptions for incumbents; enforcement that targets small players; regulator-industry revolving door; “guidance” functioning as law.
**Mitigations:** `CAP-7` rulemaking quality + public regulatory inventory; `ACC-5` influence transparency; publish decisions/reasons/data; meaningful appeal (`LAW-5`); procedural fairness norms for competition enforcement; clear separation of ownership and regulation for SOEs (`CAP-8`). See `13-regulation-utilities-and-soes.md`.

