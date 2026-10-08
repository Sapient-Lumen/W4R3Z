# Active-window proof page — 50,000-file ceiling, suspension exceptions, and queue rebuild

## Purpose

Give the operator one proof page for the real scope and ceiling of download prioritization.
This page exists because `prioritized` is not the same as `the whole backlog is under this rule right now`.

## Proof targets

The page must prove or deny:

1. Whether the target file currently sits inside the active prioritized window.
2. Whether the active window is below, near, or above the practical 50,000-file ceiling.
3. Whether lower-priority work was suspended for this item.
4. Whether documented exception classes limit that suspension story.
5. Whether queue rebuild is currently mutating the scheduler view.

## Required evidence blocks

### A. Admission block

Show:

- active queue size
- target admitted yes/no
- target waiting outside active window yes/no

### B. Suspension block

Show:

- lower-priority work suspended yes/no
- currently running large-file interruption yes/no
- exception class present yes/no

### C. Rebuild block

Show whether queue reconstruction is underway because of:

- size change
- mtime change
- error arrival
- item removal
- item completion

### D. Splitability block

Show whether the file is within the documented class that strictly follows prioritization or a non-splittable / exception-bearing class where cancellation rules are weaker.

## Required blocked stronger sentences

The page must explicitly refuse to imply:

- `all waiting files are currently priority-ordered`
- `this higher-priority file will start immediately`
- `lower-priority work has no surviving exceptions`
- `current queue order is stable until completion`

## Minimal summary sentence

The page should be able to emit one tight proof sentence such as:

`This file currently inherits newer-first ordering, is outside the active 50,000-file window, and therefore is not yet under live priority scheduling.`
