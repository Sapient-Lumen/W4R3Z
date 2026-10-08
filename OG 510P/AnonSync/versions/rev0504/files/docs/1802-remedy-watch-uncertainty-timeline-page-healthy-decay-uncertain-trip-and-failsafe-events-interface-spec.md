# Remedy-watch-uncertainty timeline page — healthy, decay, uncertain, trip, and fail-safe events

## Purpose

This page is the ordered event surface for how a discharged case's guard moved from healthy proof into uncertainty, fail-safe, and recovery or collapse.
It exists so later readers can see uncertainty age and fail-safe timing directly rather than reconstructing them from scattered warnings and support steps.

## Event types

The timeline must support at least these event kinds:

- watch-health proven
- uncertainty budget armed
- signal path degraded
- notification path disabled
- background priority lost
- service notification loss declared
- watcher fallback activated
- rescan-only discovery declared
- restart-required discovery declared
- uncertainty declared
- uncertainty grace started
- uncertainty over budget
- automatic narrowing fired
- automatic re-fence fired
- manual fail-safe requested
- manual fail-safe completed
- fresh proof restored
- uncertainty collapsed

## Timeline queries

The page must answer:

- when did uncertainty first start?
- when did it cross the grace budget?
- what signal path degraded first?
- when did the automatic fail-safe fire?
- when was manual re-fence still required?
- when did the stronger ordinary-life sentence become honest again?

## View modes

The page must provide:

- all-events view
- uncertainty-trigger view
- budget-crossing view
- fail-safe execution view
- cohort-filtered view
- recovery-only view
