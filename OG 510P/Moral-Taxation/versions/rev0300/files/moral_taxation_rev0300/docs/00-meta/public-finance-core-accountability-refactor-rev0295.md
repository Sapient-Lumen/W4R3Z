# Public-finance-core accountability refactor — rev0295

Rev0295 converts the `public_finance_core` actor-accountability family from broad public-body placeholders into route-specific accountability maps. This was the largest remaining specificity debt after the tax-administration-access and controller-AI passes.

## Why this was the risky slice

Public-finance-core routes sit at the archive's waist. They decide whether an object is a tax, fee, mandate, public option, remedy, subsidy, base overlap, incidence claim, proceeds route, disclosure duty, or review trigger. If those routes keep generic profiles, the archive can sound precise while still failing to say who actually controls the burden, who benefits from opacity, who holds the channel, who bears the cost, and which public fallback duty survives.

The main failure modes were:

1. **public-body smearing** — legislature, budget office, agency, court, remitter, vendor, and beneficiary all collapse into one public-policy actor;
2. **beneficiary invisibility** — the route names a broad moral object but not the firm, sector, fund, intermediary, agency, or incumbent that captures the advantage;
3. **instrument-label capture** — tax, fee, mandate, subsidy, compensation, and public-option labels are accepted before incidence, benefit nexus, and repair channel are traced;
4. **proceeds and remedy theater** — money or relief is described as repair without evidence of recipient, timing, anti-supplantation, or escalation;
5. **model/table finality** — incidence tables, distributional averages, thresholds, proxies, and net-stack summaries are treated as answers rather than contested evidence controlled by named actors.

## Concrete changes

| Metric | Before rev0295 | After rev0295 |
|---|---:|---:|
| `public_finance_core` profiles | 44 | 44 |
| public-finance-core beneficiary placeholders | 41 | 0 |
| public-finance-core generic `benefit_or_rent_trace` evidence bundles | 44 | 0 |
| archive-wide beneficiary placeholders | 95 | 54 |
| archive-wide generic evidence bundles | 117 | 73 |
| primary-accountable actor categories | 50 | 92 |

## Clusters completed

The pass specializes all 44 public-finance-core profiles, including:

- base ordering, overlap, creditability, and non-substitution;
- incidence evidence and protected-burden repair;
- proceeds visibility, local share, earmarking, and anti-supplantation;
- instrument choice across tax, fee, mandate, ban, public option, and compensation;
- remedy traceability, escalation, and proceeds integrity;
- automaticity, take-up, threshold cliffs, and delivery sync;
- net fiscal stack disclosure, tax-expenditure audit, and hidden substitution;
- democratic authorization, consultation, and affected voice;
- beneficial-ownership/controller-chain and responsibility-chain routing;
- measurement cadence, proxy graduation, verification intensity, reliance, review triggers, and standing.

## Design rule

A public-finance-core route now has to name:

1. the actor with legal, budgetary, modeling, classification, channel, or fund-control power;
2. the beneficiary or rent recipient that gains from the category choice, opacity, undermeasurement, stale rule, hidden subsidy, proceeds diversion, or failed remedy;
3. the bottleneck, channel, model, ledger, formula, queue, or legal gate that gives the actor practical control;
4. the protected burden bearer if the route is wrong; and
5. the evidence packet that can prove or rebut the assignment.

## New release gate

`tools/audit_actor_accountability_profiles.py` now rejects public-finance-core profiles that keep a generic beneficiary placeholder, keep generic benefit-trace evidence, leave the bottleneck unidentified, or fail to include route-specific responsibility bases. It also gives extra checks to instrument choice, incidence evidence, and proceeds visibility because those are the most reusable failure surfaces.

## Remaining specificity debt

After rev0295, the largest unresolved placeholder families are labor/care/benefits, legal-enforcement-penalty, environment/climate/commons, social-floor public services, cross-border reporting, regulated networks/platforms, and release-integrity/currentness. The next high-leverage pass should probably take `legal_enforcement_penalty` or `environment_climate_commons`, because those families can misassign coercive burden or non-compensable harm if accountability remains generic.
