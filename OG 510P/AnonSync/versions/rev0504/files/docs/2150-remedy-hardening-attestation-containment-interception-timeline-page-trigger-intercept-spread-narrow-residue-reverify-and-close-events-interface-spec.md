# Remedy-hardening-attestation containment-interception timeline page — trigger, intercept, spread, narrow, residue, reverify, and close events

## Purpose

This page makes containment behavior legible over time.
It exists so the archive can show not only that relapse risk was known, but also whether a trigger was intercepted, partially spread, narrowed, cleaned up, or left with residue.

## Timeline events the page must support

The page must support at least:

- clean state established
- watch horizon opened
- stale trigger emitted
- automatic interception fired
- spread observed before interception
- pause / scheduler window entered
- offline peer reconnected
- archive restore replay attempted
- read-only divergence created fork
- disconnect applied to device
- UI removal performed
- residue discovered on device or audience slice
- cleanup / re-remediation completed
- clean state re-verified
- containment horizon closed

## Event requirements

Each event row must preserve:

- timestamp or bounded time window
- actor / peer / surface
- event class
- affected artifact or audience slice
- whether the event widened spread, narrowed it, contained it, or only observed it
- whether the strongest honest containment sentence changed

## Closure rule

The timeline must not allow `containment horizon closed` unless it also records:

- which channels never became interceptable
- what residue still remained at closure
- what evidence justified closure anyway
- what stronger sentence stayed blocked despite closure

## Visual emphasis

The page should visually distinguish:

- trigger events
- interception events
- spread-before-intercept events
- residue-discovery events
- cleanup / re-verification events
- final closure event
