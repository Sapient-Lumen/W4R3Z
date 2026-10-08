# Action sufficiency proof page — protective vs irreversible acts and earned scope

## Purpose

This page is the durable proof object for the strongest typed act honestly executed in the case.
It exists so later operators can see not merely who signed, but what exact act was truly earned, what scope it touched, and which stronger irreversible acts remained blocked.

## Sentences this page may support

- `fund receipt acknowledged; no settlement accepted`
- `provisional settlement accepted for undisputed core only`
- `probation lifted for this creditor slice; future-burst normalization still blocked`
- `final waiver executed after unanimity and cooling window`
- `protective reopen executed immediately; irreversible closure rescinded pending review`

## Mandatory proof blocks

### A. Executed-act block

- action family executed
- execution time
- coalition used
- reversibility class
- strongest sentence earned by the execution
- stronger sentence still blocked at execution time

### B. Scope block

- creditor slice or residue touched
- disputed residue included or excluded
- probation effect
- future-burst effect
- whether reopen rights survive
- whether predecessor acts were ratified, superseded, or left untouched

### C. Preconditions block

- signer threshold satisfied
- named seats satisfied
- conflict-freeze absent or adjudicated
- cooling window satisfied if required
- contest window opened or waived if applicable
- evidence horizon still valid at execution time

### D. Non-earned block

- stronger acts not earned
- exact reason each stronger act was not earned
- weaker acts that would still remain valid if this proof is reopened
- whether execution can be revised without fraud or only via reopen path
- exact event that would narrow or withdraw this proof

### E. Audit block

- decisive signatures and timestamps
- decisive objections preserved
- decisive cooling-window evidence
- decisive adjudication reference if used
- decisive successor or delegation facts if used

## Required badges

- `receipt-only`
- `provisional-settlement`
- `capped-settlement`
- `final-waiver-executed`
- `probation-lifted`
- `future-burst-normalized`
- `protective-freeze-executed`
- `reopen-executed`
- `cooling-satisfied`
- `stronger-act-blocked`

Badges must stack instead of collapsing meaning.
For example, `probation-lifted` may coexist with `future-burst-normalized` absent, and `reopen-executed` may coexist with `receipt-only` preserved in lineage.

## Proof obligations

- prove the action family separately from signer validity
- prove the affected scope separately from the existence of a settlement payment
- prove cooling satisfaction separately from coalition sufficiency
- preserve stronger blocked acts even when one weaker act is fully earned
- preserve surviving reopen power unless the exact act row extinguished it

## Stronger-sentence guard

This page may say `provisional settlement accepted for undisputed core after quorum; disputed residue waiver and future-burst normalization remain blocked`.
It may not say `all downstream rights cleared` until those stronger typed acts were independently earned.
