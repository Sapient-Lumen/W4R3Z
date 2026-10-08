# Remedy-hardening-attestation recurrence-watch timeline page — clean verified, offline return, archive restore, rescan detect, and horizon-close events

## Purpose

This page makes recurrence risk legible over time.
It exists so the archive can show not only when a clean state was established, but also whether later events reopened, threatened, or reconfirmed that state.

## Timeline events the page must support

The page must support at least:

- stale artifact found
- corrected replacement adopted
- clean state verified
- watch horizon opened
- pause or scheduler window entered
- offline peer edited material
- peer reconnected and precedence replayed
- archive version restored
- restored file re-archived on later rescan
- watcher degraded / rescan-only posture entered
- manual rescan triggered
- read-only local edit suspended future sync
- conflict artifact emitted
- recurrence repaired
- horizon closed

## Event requirements

Each event row must preserve:

- timestamp or bounded time window
- actor / peer / surface
- event class
- affected artifact or slice
- whether the event widened recurrence risk, narrowed it, or merely observed it
- whether the stronger recurrence-safe sentence changed

## Horizon-close rule

The timeline must not allow `horizon closed` unless it also records:

- what channel set was still open at closure
- what evidence justified closure anyway
- what stronger sentence stayed blocked despite closure

## Visual emphasis

The page should visually distinguish:

- clean-establishing events
- channel-opening events
- detection-only events
- containment / repair events
- final horizon-close event
