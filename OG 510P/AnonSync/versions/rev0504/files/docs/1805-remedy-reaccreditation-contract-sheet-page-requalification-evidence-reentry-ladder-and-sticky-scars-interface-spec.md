# Remedy-reaccreditation contract sheet page — requalification evidence, re-entry ladder, and sticky scars

## Purpose

This page is the operator's compact contract for when a previously uncertain, fail-safe-bounded, or re-fenced case may honestly re-enter guarded ordinary life.
It exists so the product can distinguish `a recovery action happened` from `the case is requalified to re-enter under an honest stronger sentence`.

## Core fields

- case identifier
- source remedy-watch-uncertainty receipt identifier
- current remedy-reaccreditation posture rung
- current fence or fail-safe posture
- original uncertainty cause family
- cause-remediation status
- restored signal-path class
- required requalification cohort
- current requalification coverage achieved
- latest proof freshness ceiling
- latest end-to-end drill freshness
- current re-entry authority class
- automatic re-entry allowance status
- manual re-entry obligation status
- sticky-scar class
- tightened ongoing watch budget, if any
- strongest honest current re-entry sentence
- strongest blocked stronger ordinary-life sentence
- next strengthening trigger
- next weakening trigger

## Remedy-reaccreditation posture rungs

The page must model at least these distinct rungs:

- fail-safe contained; requalification not started
- signal path restored; cause not remediated
- cause remediated; proof stale
- named-cohort requalification only
- required-cohort proof pending re-entry authority
- re-entry authority pending manual release
- re-entry authorized with sticky scars
- re-entry authorized under tighter budget
- re-entry completed; scar retained
- requalification collapsed; case remains fenced

## Required distinctions

The page must keep these truths separate:

- signal path restored versus uncertainty cause remediated
- cause remediated versus required-cohort proof refreshed
- required-cohort proof refreshed versus re-entry authorized
- automatic re-entry permitted versus automatic re-entry executed
- soft fail-safe narrowing versus full re-fence recovery
- re-entry with sticky scars versus scar-cleared ordinary life
- one healthy-looking lane versus required-cohort requalification

## Operator promises

The contract sheet must let the operator say things like:

- `the Android background lane recovered, but the case remains fenced because required-cohort proof is still stale`
- `service-side restart and force rescan restored visibility, but re-entry stays blocked until the original uncertainty cause is judged remediated`
- `required-cohort proof returned and manual re-entry authority approved guarded ordinary life under a tighter watch budget`
- `automatic re-entry was not allowed because the case had escalated to full re-fence rather than soft narrowing`
- `the case re-entered ordinary life honestly, but only with a sticky scar that keeps faster decay and lower uncertainty budget active`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- uncertainty still active
- cause not remediated
- required-cohort proof stale
- re-entry authority missing
- manual release still required
- sticky scar not yet acknowledged
- tighter budget not armed
- evidence basis too weak to requalify
