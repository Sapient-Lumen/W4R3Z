# Remedy-watch-health timeline page — arming, probe, drill, degrade, trip, and re-fence events

## Purpose

This page is the ordered event surface for how a discharged case's relapse guard proved, lost, or regained credibility over time.
It exists so later readers can see freshness decay and response-budget failures directly rather than reverse-engineering them from scattered traces.

## Event types

The timeline must support at least these event kinds:

- surveillance armed
- watch-health probe scheduled
- canary probe started
- canary probe passed
- canary probe failed
- end-to-end drill started
- end-to-end drill passed inside budget
- end-to-end drill exceeded budget
- platform blind spot declared
- runtime blind spot declared
- watcher fallback activated
- logging enabled
- logging disabled
- evidence freshness expired
- relapse signal observed
- threshold met
- automatic re-fence fired
- manual re-fence required
- watch-health restored
- watch-health collapsed

## Timeline queries

The page must answer:

- when was the last successful required-cohort probe?
- when was the last successful required-cohort drill inside budget?
- when did the guard become stale?
- what degraded the strongest watch-health sentence?
- when did re-fence response first exceed budget?
- when did the case regain credibility?

## View modes

The page must provide:

- all-events view
- probe-only view
- drill-only view
- degrade-and-collapse view
- re-fence response-budget view
- cohort-filtered view
