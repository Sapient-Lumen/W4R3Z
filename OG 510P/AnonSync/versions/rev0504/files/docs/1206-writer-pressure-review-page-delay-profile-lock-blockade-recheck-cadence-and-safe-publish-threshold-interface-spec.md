# Writer-pressure review page — delay profile, lock blockade, recheck cadence, and safe publish threshold

## Purpose

Review a concrete file or path family before the interface states that the change is merely `late`.
This page exists because delayed publication and blocked publication are not the same truth.

## This review must distinguish

- file-class delay intentionally buffering a likely in-progress writer
- hard lock blockade where Sync cannot access the file
- unknown owner-of-lock cases
- missed-notification cases where the file may already be quiescent but has not yet been rediscovered
- substrate or permission cases that masquerade as lock trouble

## Inputs the page must collect

### Writer / hold facts

- affected path or path set
- file extension or tool family
- active delay profile, if any
- configured quiet-window duration
- whether the file is currently listed as locked
- whether the locking application is known or unknown

### Retry and discovery facts

- current `recheck_locked_files_interval`
- next scheduled retry
- whether live notifications are healthy
- whether folder rescans are currently carrying the discovery burden
- whether a manual rescan has already been attempted

### Publication facts

- last stable size/mtime observation
- whether the file has changed again during the hold
- whether any earlier candidate was already published
- whether a later publish would still need chronology review

## Decision ladder

### Branch 1 — intentional quiescence hold

Use this branch when a file-class delay is active and there is no hard access failure.
The page should show:

- why the file is being buffered
- the quiet-window countdown
- the next release point
- that buffering reduces conflict pressure but does not certify content correctness

### Branch 2 — lock-blocked

Use this branch when the file cannot be accessed due to a lock.
The page should show:

- that the file is not merely delayed
- the next retry time
- whether the lock owner is unknown
- that `locked` is stronger than `still editing maybe`

### Branch 3 — detection gap with no hard block

Use this branch when the file may have changed but live notification evidence is missing.
The page should show:

- whether periodic rescan is expected to rediscover it
- whether manual rescan or manual touch is the next honest act
- that the product is missing observation certainty, not necessarily access

### Branch 4 — substrate or permission suspicion

Use this branch when a mounted share, network path, or local permission floor may be causing the apparent stall.
The page should show:

- why lock semantics may be misleading
- whether path repair or permission repair is the next rung
- that publication safety is blocked on substrate truth, not editor quiet alone

## Future-risk mitigation panel

The page must include a separate panel for recurrence, not merged with the current verdict.
It must offer:

- `Review or change file-class delay profile`
- `Leave delay unchanged`
- `Escalate to substrate or permission repair`
- `Do not recommend delay for this file kind`

The panel must say plainly that delay policy is about future pressure management, not retroactive proof that the current file is the right winner.

## Required warnings

- `Delay-hold is not the same as lock blockade.`
- `Lock owner may be unknown even when lock state is known.`
- `Retry cadence is not proof that publication will succeed on the next pass.`
- `Manual rescan or touch changes observation, not authorship.`
- `Quiet-window completion is weaker than chronology correctness.`

## Review outputs

- current hold-or-block class
- next retry or release trigger
- safe-publish threshold
- substrate suspicion flag
- optional future delay recommendation
