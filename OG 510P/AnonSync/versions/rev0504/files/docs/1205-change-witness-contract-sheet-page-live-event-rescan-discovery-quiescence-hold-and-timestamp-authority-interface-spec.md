# Change-witness contract sheet page — live event, rescan discovery, quiescence hold, and timestamp authority

## Purpose

Give the operator one first surface for any serious `this file changed` or `this file still has not moved` claim.
The page must stop the product from collapsing detection witness, intentional waiting, blocked access, and timestamp-authority downgrade into one vague status badge.

## The page must answer

1. How was this change detected?
2. Is publication waiting intentionally, blocked, or already past that phase?
3. What timestamp authority is currently in force?
4. What next event would advance the file?
5. What stronger sentence is blocked?

## Core model

### A. Change-witness class

Represent exactly one current class:

- **Live watcher event observed**
- **Periodic rescan discovery**
- **Manual rescan discovery**
- **Manual touch / induced change evidence**
- **Detection still uncertain**

### B. Publication posture

Represent exactly one current class:

- **Ready to publish**
- **Quiescence hold**
- **Lock-blocked**
- **Waiting on recheck**
- **Already published / not pending**

### C. Timestamp-authority class

Represent exactly one current class:

- **Disk mtime and authoritative time aligned**
- **Disk mtime trusted but chronology not yet settled**
- **Database-only authoritative timestamp**
- **Timestamp trust degraded / manual review required**

### D. Trigger-to-advance

Represent the next honest step, never as folklore:

- quiet window expires
- lock clears
- retry interval elapses
- rescan runs
- manual touch or manual rescan required
- permission or substrate problem must be repaired first

## Required warnings

The page must warn when:

- change discovery currently depends on periodic rescan rather than live notifications
- a file-class delay is intentionally holding publication for a quiet window
- a file is blocked by an external lock and the locking application is unknown
- the product is waiting on `recheck_locked_files_interval`
- authoritative time is in the database while on-disk mtime is not trustworthy
- the current page can explain observation and waiting but not authorship correctness

## Required blocked stronger sentences

The page must explicitly refuse to imply any of these unless separately proven:

- `the edit was seen immediately`
- `waiting means the file is safe and complete`
- `disk mtime is the full authority here`
- `manual touch proves who made the edit`
- `no live watcher means nothing important changed`

## Required outputs

This page must emit a compact contract object preserving:

- change-witness class
- publication posture
- timestamp-authority class
- next advance trigger
- current claim ceiling
- blocked stronger sentence
