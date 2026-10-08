# Remedy-surveillance timeline page — discharge watch, relapse escalation, and re-fence events

## Purpose

This page shows the event chain that turned a discharged case into an honestly guarded ordinary-life continuation — or failed to do so.
It exists so later readers can see where surveillance weakened: missing coverage, platform blind spots, runtime blind spots, weak delivery, missed threshold, or later relapse and re-fence.

## Required event classes

The timeline must support events such as:

- discharge released
- surveillance arming requested
- surveillance armed for named cohort
- surveillance armed for required cohort
- platform blind spot detected
- runtime blind spot detected
- notification delivery disabled
- Android background-priority degradation observed
- Linux in-UI-only watch noted
- warning family activated
- relapse signal observed
- threshold decision opened
- threshold met
- threshold not met
- automatic re-fence triggered
- manual re-fence requested
- manual re-fence executed
- surveillance collapsed
- discharge collapsed by relapse

## Timeline rules

- every event must record actor, cohort, object, and observed surveillance class
- the timeline must separate `discharged`, `surveillance armed`, `signal observed`, `threshold met`, and `re-fence executed`
- the timeline must preserve whether weakening came from platform blind spots, runtime degradation, missing signal-family coverage, or delayed authority
- the timeline must keep manual and automatic re-fence actions explicit rather than hiding them inside a final verdict

## Output sentence family

The timeline summary must support statements such as:

- `the case was discharged first, but guarded continuation stayed blocked until surveillance was armed for the required cohort`
- `the case remained only weakly guarded because Android and Linux blind spots stayed unresolved`
- `a relapse signal appeared, crossed the re-fence threshold, and triggered automatic reclose`
- `ordinary life continued briefly, then surveillance collapsed when the product lost honest coverage over the required signal families`
