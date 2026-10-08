# Stability-window contract sheet page — freshly attained, observation, and stable promotion

## Purpose

This page is the canonical declaration of when an attained effect becomes stable enough for a stronger sentence.
It exists so the product can stop pretending that `it landed once`, `the UI is quiet`, `connected peers are green`, and `the result is now safe to treat as settled` are the same truth.

The page must answer:

> for this act version and effect lane, when did attainment begin, what observation horizon applies, what regression budget is tolerated, which cohort must stay clean, what still threatens reopen, and what stronger stability sentence remains blocked?

## Mandatory stability rungs

At minimum the page must expose these rungs separately:

- freshly attained
- under stability observation
- observation-window clean so far
- connected cohort stable only
- required cohort still unobserved
- stability earned
- stability earned with tolerated residue
- reopened after regression signal
- decayed / destabilized
- stability re-earned

The implementation may add more rungs, but it may not collapse them into one generic `settled` state.

## Mandatory blocks

### A. Act-and-effect block

- source act identifier
- effect lane identifier
- source attainment proof identifier
- exact stability question this page is answering
- exact reason a stability sheet is required instead of promoting directly from attainment

### B. Observation-window block

- attainment start time
- observation start time
- minimum dwell window for stronger promotion
- whether the clock basis is trusted enough for this window
- whether the window pauses during outage, contest, or unknown-peer periods
- exact event that would restart the window

### C. Cohort-and-risk block

- required cohort for stable promotion
- merely connected cohort
- known offline or unreachable members still able to reopen the claim
- whether placeholder-only, disconnected, or archived-only members still matter
- regression sensitivity class for this act type
- tolerated noise budget, if any
- strongest blocked stronger sentence if cohort coverage is incomplete

### D. Regression-and-reopen block

- what counts as material regression
- whether late offline return can reopen
- whether restore-from-archive can reopen
- whether manual rescan discovery can reopen
- whether hidden merge, delayed watcher notice, or clock correction can reopen
- whether the system treats the event as full reopen, narrow reopen, or cosmetic churn

### E. Promotion-and-guard block

- exact sentence earned when stability is achieved
- exact stronger sentence still blocked even after stability-earned
- whether irreversible follow-on actions may now proceed
- whether a human review or adjudicator is still required
- what proof must be preserved for later review

## Required comparisons

The page must keep these comparisons explicit:

- `freshly attained` vs `under observation`
- `observation clean so far` vs `stability earned`
- `connected cohort stable` vs `required cohort stable`
- `no warning visible` vs `no regression signal exists`
- `earlier attainment preserved` vs `stronger stable sentence currently blocked`
- `reopened` vs `fully decayed`

## Required badges

- `freshly-attained`
- `under-observation`
- `connected-only-stable`
- `required-cohort-pending`
- `stability-earned`
- `stable-with-residue`
- `reopened-by-regression`
- `decayed`
- `re-earned`

Badges must stack instead of collapsing meaning.
For example, `freshly-attained`, `under-observation`, and `required-cohort-pending` may coexist when the effect landed for connected participants but a stronger stable-promotion sentence is still blocked.

## Stronger-sentence guard

This page may say `the effect is attained and has stayed clean for 47 minutes among connected participants, but one offline authority-bearing participant can still reopen the state, so stable promotion is blocked`.
It may not say `the effect is now safely settled` unless that stronger sentence is truly earned.
