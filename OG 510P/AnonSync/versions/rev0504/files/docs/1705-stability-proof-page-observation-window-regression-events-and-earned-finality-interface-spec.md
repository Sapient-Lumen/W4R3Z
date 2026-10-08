# Stability proof page — observation window, regression events, and earned finality

## Purpose

This page is the durable proof artifact for any claim that an attained effect has become stable enough to support a stronger sentence.
It exists so the product can prove not only that something landed, but that it remained acceptably intact through the required observation horizon.

## Mandatory proof fields

### 1. Source linkage

- source act identifier
- source attainment proof identifier
- source time-authority proof identifier
- source cohort definition
- source stability rule version

### 2. Window evidence

- attainment timestamp
- observation-start timestamp
- observation-end or current timestamp
- trusted time basis used for the window
- pauses, resets, or exclusions applied to the window
- whether the window is complete or still running

### 3. Cohort evidence

- required cohort for stable promotion
- observed cohort during the window
- members missing from observation
- members whose offline state still carried reopen power
- whether connected-only evidence was used and why that is weaker

### 4. Regression evidence

- regressions observed during the window
- whether each regression was cosmetic, narrow, or material
- whether any late offline return occurred
- whether any rescan-discovered drift occurred
- whether any restore-from-archive event occurred
- whether any hidden-task completion changed the verdict

### 5. Promotion verdict

- smallest honest sentence now earned
- stronger sentence still blocked
- whether the claim is `stable-earned`, `stable-with-residue`, `reopened`, or `decayed`
- next event that could strengthen the claim
- next event that could weaken it again

## Required proof statements

The page must be able to state sentences like these:

- `the effect was attained at T1 but remains under observation because two required participants are still offline`
- `the effect stayed clean for the full typed dwell window across the required cohort and earned stable promotion at T2`
- `the effect had earned stable promotion, but a late offline-return overwrite at T3 reopened the claim while preserving the earlier attainment record`
- `the effect is stable only for the connected operational cohort and is not yet stable for the required fairness cohort`

## Proof ceiling

This page may prove `stability earned for the required cohort under the current rule version`.
It may not on its own prove broader finality such as irrevocable closure, waiver, or normalization unless the exact action matrix independently allows that stronger sentence.

## Preservation rules

The proof must preserve:

- the earlier attainment verdict
- the exact stability rule version used
- the window timing basis
- all material regression events
- why any residue was tolerated
- what stronger sentence remained blocked at the time of issuance

## Reopen rule

If later evidence shows that the observation window was untrusted, the cohort was incomplete, or a material regression was missed, this page must downgrade into explicit reopened proof rather than silently disappearing.
