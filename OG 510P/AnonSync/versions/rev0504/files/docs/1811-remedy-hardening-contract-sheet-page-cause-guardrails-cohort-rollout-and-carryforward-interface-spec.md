# Remedy-hardening contract sheet page — cause guardrails, cohort rollout, and carry-forward

## Purpose

This page is the operator's compact contract for whether a case that already requalified for guarded ordinary life has also been hardened enough to resist recurrence of the same causal class.
It exists so the product can distinguish `we made a repair` from `we deployed durable guardrails across the surfaces that could recreate the same incident`.

## Core fields

- case identifier
- source remedy-reaccreditation receipt identifier
- triggering cause family
- current remedy-hardening posture rung
- hardening strategy class
- durable-versus-temporary-control class
- required hardening cohort
- current hardening coverage achieved
- future carry-forward surface class
- linked-identity spread exposure
- permission-topology hardening status
- config and preference rollout status
- ignore or exclusion rule rollout status, if relevant
- restart or rescan dependency still present
- strongest honest current hardening sentence
- strongest blocked stronger recurrence-safe sentence
- next strengthening trigger
- next weakening trigger

## Remedy-hardening posture rungs

The page must model at least these distinct rungs:

- cause remediated once; no durable hardening yet
- temporary workaround active only
- durable hardening drafted
- named-lane hardening deployed
- required-cohort hardening pending carry-forward closure
- required-cohort hardening deployed
- required-cohort hardening proven active
- recurrence budget narrowed but not fully hardened
- recurrence-hardened discharge achieved
- hardening collapsed or rolled back

## Required distinctions

The page must keep these truths separate:

- cause remediated once versus durable guardrail deployed
- durable guardrail deployed versus required-cohort rollout complete
- required-cohort rollout complete versus future carry-forward surface closed
- config changed versus hardening proven active in the exact risky lane
- one linked device or one folder type protected versus all relevant topology protected
- temporary operator habit versus durable system constraint
- narrower recurrence budget versus recurrence-hardened discharge

## Operator promises

The contract sheet must let the operator say things like:

- `the immediate cause was fixed, but linked-device carry-forward still blocks the stronger recurrence-safe sentence`
- `IgnoreList and folder-preference hardening were deployed only to the named high-risk lane, so required-cohort hardening remains incomplete`
- `the case re-entered guarded ordinary life under a hardening debt because the durable policy rollout is still pending on one peer class`
- `permissions were tightened for Advanced folders, but Standard-folder onward-sharing still keeps full recurrence-hardening blocked`
- `the causal guardrail is now durable, cohort-wide, and proven active, so recurrence-hardened discharge is honest`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- workaround only
- durable guardrail not deployed
- required cohort not covered
- carry-forward surface still open
- linked-identity spread still exposed
- permission topology not hardened
- rescan or restart dependency still required
- evidence basis too weak to claim recurrence hardening
