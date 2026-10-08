---
status: case_template
claim_kind: program_rule
route_role: case_work_core
canonical_anchor: false
route_refs:
- case_work_core
- case_calibration_core
supersedes: null
depends_on: []
source_refresh_due: 2026-11-30
---

# Case memo template

## What this template is for

Use this file to turn the archive from doctrine into judgment. A case memo should be short enough to compare, but strict enough that a flattering national average, a popular instrument, or a single source cannot carry the verdict.

Use this template with [`../docs/20-program/case-work-decision-path.md`](../docs/20-program/case-work-decision-path.md), [`../docs/20-program/minimum-evidence-pack-for-case-work.md`](../docs/20-program/minimum-evidence-pack-for-case-work.md), [`../docs/20-program/scoreboard-spec.md`](../docs/20-program/scoreboard-spec.md), [`../docs/20-program/scoreboard-calibration-matrix.md`](../docs/20-program/scoreboard-calibration-matrix.md), [`../docs/20-program/threshold-moment-registry.md`](../docs/20-program/threshold-moment-registry.md), and [`../docs/20-program/source-order-and-conflict-resolution.md`](../docs/20-program/source-order-and-conflict-resolution.md).

## Header

- **Case:** `country / region / program`
- **Memo ID:** `case-slug-revision-date`
- **Scope:** national / subnational / sector / program
- **Case type:** `rich_asset_price_democracy / social_democratic_housing_constrained / public_housing_asset_state / middle_income_land_legibility / resource_dividend_public_wealth / climate_insurance_stress_surface / other`
- **Calibration class:** `case_portfolio_seed / stress_surface_seed / direct_case_read / stale_case`
- **Status:** seed / active / provisional / stale / retired
- **Date:** `YYYY-MM-DD`
- **Authoring posture:** archive application, not advocacy brief
- **Freshness window:** which data are current, aging, or missing
- **Primary source order:** list the source families that govern each major surface
- **Machine scoreboard:** companion JSON file, if any

## Verdict strip

Fill this first, then revise it after the evidence table.

| Field | Entry |
|---|---|
| Constitutional verdict | near-ideal / acceptable / vulnerable / correction-required / emergency repair / captured |
| Mode | prevention / correction / emergency / anti-oligarchy / mixed |
| Dominant breach | the single breach driving the opening package |
| Fastest washout | the channel most likely to reabsorb gains |
| Threshold moments | the life-course, ownership, place, or institutional moments that drive the verdict |
| Scoreboard status | complete / proxy-heavy / data-blocked / stale |
| Group/person veto | none / warning / active veto / data-blocked |
| Public-counterweight reading | strong / usable / thin / patronage-routed / negative |
| Top-tail rule risk | low / watch / high / captured |
| Confidence | high / medium / low / proof-debt |
| Reopening trigger | the fact that would force a reread |


## Threshold moments

Use this section to keep the memo from becoming only a national-share reading. Name at least three threshold moments from [`../docs/20-program/threshold-moment-registry.md`](../docs/20-program/threshold-moment-registry.md). A threshold moment is a point where the wealth order becomes real or false for a person, household, group, place, or public institution.

| Moment | Read | Evidence | Routing consequence |
|---|---|---|---|
| first foothold | open / family-gated / late / debt-backed / data-blocked |  |  |
| shock survival | real / paper / forced-self-insurance / data-blocked |  |  |
| place exit or repair | open / trapped / self-eroding / data-blocked |  |  |
| public claimability | rule-bound / rationed / patronage-routed / exclusionary / data-blocked |  |  |

## Minimum evidence table

Use the table below. Add rows only when they can change verdict, package, rails, or confidence.

| Surface | Minimum evidence | Reading | Source IDs | Routing consequence |
|---|---|---|---|---|
| Private wealth shares | bottom 50, middle 40, next 9, top 1, top 0.1 where available |  |  |  |
| Public/social counterweight | net public wealth or functional social-wealth proxy |  |  |  |
| Lower-half floor | liquidity, positive net wealth, debt distress, claimability, asset rules |  |  |  |
| Early footholds | young-adult entry, family-backed thresholds, inheritance timing, first secure tenure |  |  |  |
| Group/person closure | subgroup medians, title/control, tenure, pensions, land, business access |  |  |  |
| Housing/land washout | rent burden, price-income, supply, displacement, local ownership concentration |  |  |  |
| Debt/fee washout | debt-service stress, garnishment, insolvency restart, fee drag |  |  |  |
| Top-tail/rule conversion | political finance, lobbying, beneficial ownership, media, procurement, rescue terms |  |  |  |
| Threshold moments | deposit/guarantee, repair, care, legal proof, safe exit, business entry, public claim conversion |  |  |  |
| Climate/insurance | premium, deductible, insurability, hazard exposure, repair burden |  |  |  |
| Digital/intangible | compute, data, IP, platform rents, AI capital, private-market allocation |  |  |  |
| Dynastic infrastructure | trusts, family offices, DAFs, foundations, estate/gift channels |  |  |  |
| Macro-financial channel | asset-price stabilization, housing credit, QE/APP distributional effects |  |  |  |
| Rails | registries, valuation, enforcement, take-up, appeals, anti-capture safeguards |  |  |  |

## Dominant-breach selection

Name exactly one dominant breach for the opening package. A memo may record several major failures, but it should not let package choice dissolve into a list.

Choose the breach that is:

1. morally central under the archive's dependency/closure/rule test;
2. large enough to block certification;
3. live now, not merely historical;
4. tractable enough that a real opening package can reduce it;
5. connected to the fastest washout channel.

If two breaches tie, choose the one whose repair also weakens the other. If neither does, mark the case **mixed mode** and explain the sequencing.

## Opening package

Write the package as a sequence, not a wish list.

1. **First lane:** the reform lane that directly closes the dominant breach.
2. **Second lane:** the reform lane that blocks the fastest washout.
3. **Rail lane:** the minimum registry, enforcement, budget, claimability, or anti-capture rail needed before the first two lanes can work.
4. **Hardening lane:** how gains become ratchets rather than one-cycle relief.
5. **Monitoring lane:** the indicators that decide whether to reroute.

Do not say **wealth tax**, **baby bonds**, **housing supply**, **public fund**, **inheritance tax**, **competition**, or **benefits** as slogans. State which breach the instrument closes and which false pass it avoids.

## Case pressure on doctrine

Every memo should say whether it changes the archive.

| Question | Answer |
|---|---|
| Does this case expose a missing variable? |  |
| Does it reveal that a threshold is too soft or too hard? |  |
| Does it create a new false-pass label? |  |
| Does it demote an existing rule? |  |
| Does it merely instantiate existing doctrine? |  |

A single case should normally instantiate doctrine, not rewrite it. Doctrine changes require cross-case recurrence or a direct contradiction of a canonical anchor.

## Scoreboard instance

Every active case should have a companion JSON scoreboard unless the memo is explicitly marked `data-blocked`. The scoreboard should use [`../docs/20-program/scoreboard-schema.json`](../docs/20-program/scoreboard-schema.json), record proxy status honestly, and state which variables can move verdict, mode, or package.

## What would change the verdict

End with a falsifiable update rule:

- What evidence would upgrade the case?
- What evidence would downgrade it?
- Which missing data currently blocks confidence?
- Which time window should be used for recertification?

## Compact closing form

Use this one-paragraph closing form for comparability:

> **Verdict:** `[case]` is `[verdict]` in `[case type]` mode because `[dominant breach]` remains live at `[threshold-moment read]` despite `[real gains]`. The opening package should lead with `[first lane]`, add `[second lane]` to stop `[fastest washout]`, and install `[rail lane]` before harder measures are treated as credible. The verdict should reopen if `[reopening trigger]`.
