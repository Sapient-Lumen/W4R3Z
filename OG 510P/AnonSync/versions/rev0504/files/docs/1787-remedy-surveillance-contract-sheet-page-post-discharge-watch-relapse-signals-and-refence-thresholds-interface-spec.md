# Remedy-surveillance contract sheet page — post-discharge watch, relapse signals, and re-fence thresholds

## Purpose

This page is the operator's compact contract for whether a discharged case is still being watched strongly enough to remain in ordinary life.
It exists so the product can distinguish `quarantine released` from `quarantine released and still guarded against relapse with an honest re-fence threshold`.

## Core fields

- case identifier
- source remedy-discharge receipt identifier
- current remedy-surveillance posture rung
- intended authoritative object identifier
- current ordinary-lane scope
- required surveillance cohort
- actually armed surveillance cohort
- platform coverage map
- runtime blind-spot map
- signal families currently armed
- current notification-delivery posture
- current history-retention posture
- current escalation authority posture
- current automatic re-fence threshold
- current manual re-fence threshold
- strongest blocked stronger ordinary-life sentence
- next strengthening trigger
- next weakening trigger

## Remedy-surveillance posture rungs

The page must model at least these distinct rungs:

- discharge released pending surveillance arming
- surveillance armed for named cohort only
- surveillance armed with platform blind spots
- surveillance armed with runtime blind spots
- surveillance armed for required cohort
- ordinary-lane continuation guarded
- relapse signal observed pending threshold decision
- relapse threshold met pending re-fence
- automatic re-fence fired
- manual re-fence required
- surveillance collapsed
- discharge collapsed by relapse

## Required distinctions

The page must keep these truths separate:

- discharge versus guarded discharge
- signal observed versus relapse sentence reached
- notification delivered versus required surveillance coverage
- required-cohort watch versus named-cohort watch
- platform blind spot versus runtime blind spot
- threshold met versus re-fence executed
- automatic re-fence versus manual re-fence

## Operator promises

The contract sheet must let the operator say things like:

- `the case was discharged, but surveillance is only armed for the desktop operations cohort, so stronger ordinary-life claims remain blocked`
- `Android background priority is degraded and Linux relies on in-UI visibility, so surveillance remains armed with platform blind spots`
- `a relapse signal was observed, but the re-fence threshold was not yet met, so the case stays guarded rather than collapsed`
- `the re-fence threshold was met and automatic reclose fired before wider harm resumed`
- `the case remained in ordinary life only because the named surveillance cohort, threshold rule, and escalation authority all remained live`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- surveillance not yet armed
- required cohort not fully covered
- platform blind spots still live
- runtime blind spots still live
- signal family not covered
- escalation authority not armed
- automatic re-fence unavailable
- history or notification basis too weak for the stronger sentence
