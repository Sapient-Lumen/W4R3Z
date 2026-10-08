# Remedy-hardening-attestation downstream-effects timeline page — trigger, apply, recall, undo, compensate, and closeout events

## Purpose

This page is the event-sequenced timeline for downstream consequences after stale truth.
It exists so a later operator can see not just the final posture but the order in which stale-triggered work became possible, executed, was discovered, frozen, undone, compensated, or ceilinged as irreversible.

## Event classes

The timeline must preserve at least these event types:

- stale version issued
- downstream actor subscribed or armed
- queued action created
- queued action frozen
- action execution started
- action execution completed
- stale trigger discovered
- successor or tombstone published
- undo requested
- undo completed
- human correction issued
- compensation offered
- compensation completed
- irreversibility declared
- containment applied
- restoration sentence upgraded
- restoration sentence blocked or downgraded again
- closeout or reopen event

## Required columns

Every downstream-effects timeline row must preserve at least:

- event timestamp
- event class
- actor or cohort
- triggering version token
- effect class
- reversibility class at that moment
- evidence source
- resulting restoration floor
- resulting blocked stronger sentence, if any

## Fixed rendering order

Every downstream-effects timeline page must render the same sections in the same order:

1. **Version and trigger chronology**
2. **Execution and discovery chronology**
3. **Undo and compensation chronology**
4. **Irreversibility, containment, and restoration-floor changes**
5. **Current closeout or reopen posture**

## Hard rules

The page must never silently collapse:

- trigger time and discovery time
- undo requested and undo completed
- compensation offered and compensation accepted
- irreversibility declared and containment completed
- named-cohort restoration and global restoration closure

## Minimum operator questions answered

The page must let a later operator answer, without hunting across other pages:

- when the stale version first became capable of causing downstream action
- when the first known downstream action actually executed
- whether new triggers were blocked before or after that point
- when undo, correction, compensation, or irreversibility declarations happened
- whether the current restoration sentence is newer than the latest unresolved downstream-effect event
