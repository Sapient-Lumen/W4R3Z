# Remedy-watch-uncertainty contract sheet page — confidence decay, fail-safe, and re-fence floor

## Purpose

This page is the operator's compact contract for what happens when a discharged case's guard loses freshness, coverage, or trustworthy signal paths.
It exists so the product can distinguish `watch looked healthy recently` from `watch uncertainty is bounded and fail-safe behavior is still trustworthy`.

## Core fields

- case identifier
- source remedy-watch-health receipt identifier
- current remedy-watch-uncertainty posture rung
- current ordinary-lane scope
- required guarded cohort
- uncertainty-declared cohort
- current uncertainty-budget ceiling
- current uncertainty age
- signal-path degradation class
- discovery fallback class
- current platform blind-spot map
- current runtime blind-spot map
- current rescan or restart dependency map
- automatic fail-safe policy class
- automatic fail-safe execution status
- manual fail-safe obligation status
- strongest blocked stronger ordinary-life sentence
- next strengthening trigger
- next weakening trigger

## Remedy-watch-uncertainty posture rungs

The page must model at least these distinct rungs:

- watch health current and uncertainty budget armed
- uncertainty budget shrinking
- uncertainty declared for named cohort only
- uncertainty declared for required cohort
- signal path degraded but inside grace budget
- uncertainty over budget pending fail-safe
- automatic fail-safe narrowed permissions
- automatic fail-safe re-fence fired
- manual fail-safe required
- uncertainty resolved by fresh proof
- uncertainty collapsed into unguarded ordinary-life exposure

## Required distinctions

The page must keep these truths separate:

- recent watch-health proof versus bounded uncertainty handling
- named-cohort uncertainty versus required-cohort uncertainty
- degraded signal path inside grace budget versus uncertainty over budget
- automatic fail-safe configured versus automatic fail-safe executed
- narrowed permissions versus full re-fence
- manual fail-safe obligation versus actual manual re-fence completion
- stale evidence versus declared uncertainty

## Operator promises

The contract sheet must let the operator say things like:

- `watch-health proof was recent, but the Linux lane went uncertain and is still inside a short grace budget before automatic narrowing fires`
- `Android background priority loss pushed the required cohort into uncertainty, so ordinary-life claims are now blocked unless the automatic fail-safe executes`
- `the case stayed honest because watcher fallback only affected a named lane, not the required cohort`
- `service notification loss plus restart-only discovery made the required cohort uncertain, so automatic re-fence fired before the stronger sentence could remain live`
- `fresh proof cleared the uncertainty and restored the stronger guarded-ordinary-life sentence`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- uncertainty not yet declared
- uncertainty declared but no fail-safe policy
- uncertainty inside grace budget only
- uncertainty over budget
- automatic fail-safe not executed
- manual fail-safe still required
- required cohort uncertainty unresolved
- evidence basis too weak to clear uncertainty
