# Profile drift timeline page — revision bump, field pin, freeze, branch, and rejoin events

## Purpose

This page preserves the history that makes profile conformance legible later:

> when did this subject stop being live-bound, which profile revision was current then, which fields were pinned or frozen, and when did the subject rejoin or branch away?

## Core decision

Every serious reusable-policy system must preserve one **Profile drift timeline**.
The page owns:

- profile revision chronology
- binding-class transitions
- field-pin and unpin events
- freeze and branch events
- rejoin events
- blocked-coverage events

## Event classes

The timeline must distinguish at least:

- `profile created`
- `profile revision published`
- `subject live-bound`
- `field pinned`
- `field unpinned`
- `snapshot captured`
- `branch created`
- `subject rejoined live profile`
- `world became unsupported`
- `world became supported`
- `profile retired`
- `receipt emitted`

## Fixed page order

1. timeline strip
2. revision spine
3. subject binding transitions
4. field-pin ledger
5. branch-and-rejoin ledger
6. drift receipt

### 1) Timeline strip

Show:

- canonical profile id
- focused subject or cohort id
- timeline scope: `profile-wide`, `subject`, `cohort`
- current revision id
- current binding class
- current drift verdict

### 2) Revision spine

For each profile revision show:

- revision id
- publication time
- changed fields
- activation class
- subject counts that auto-adopted
- subject counts that did not adopt because of pins, snapshots, branches, or unsupported worlds

### 3) Subject binding transitions

For the focused subject or cohort show the chronology of:

- first bind
- detach to pins
- snapshot capture
- branch creation
- rejoin
- retirement or exclusion

### 4) Field-pin ledger

For each field pin/unpin event show:

- field id
- previous state
- resulting state
- whether live inheritance was broken or restored
- whether current value changed immediately

### 5) Branch-and-rejoin ledger

Show separately:

- branch source revision
- branch target profile id
- subjects moved
- reason for branch
- rejoin preconditions
- rejoin proof emitted

### 6) Drift receipt

Emit one compact receipt with:

- profile id
- revision id in force now
- focused subject/cohort id
- current binding class
- outstanding pins
- last branch/rejoin event if any
- strongest safe drift sentence
- blocked stronger sentence

## Copy rules

- Never compress `pin`, `snapshot`, and `branch` into one generic `override` event.
- Never say `fell out of profile` without naming the actual transition class.
- Never say `rejoined` unless live inheritance is proven restored.
- Never let revision publication imply subject adoption.
- Never treat unsupported-world exclusion as a normal live drift event.

## Example strongest-safe sentence patterns

- `Profile rev13 was published on this date, but this subject did not adopt it because two fields were pinned at rev12.`
- `This subject matched profile values for a period as a frozen snapshot, not as a live binding.`
- `Branch profile ops-lan-only was created from rev11 and remains a separate lineage rather than a temporary exception.`
- `Live inheritance was restored at this event; earlier visible equality did not yet prove rejoin.`
