# BOUNDARY-CONTEXT-EXPIRY-TEST

This note tests whether `boundary_context` needs explicit expiry semantics of its own.

The archive just named `boundary_context` as a tiny optional wrapper for retained boundary explanation.
The next question is whether that wrapper now needs its own lifetime machinery.

## Question

Does `boundary_context` need an expiry rule separate from the local assessed state it accompanies?

## Source pattern

The source base points in two directions,
but they do not end up forcing the same answer.

- Telecom protection scenarios show boundary explanation matters while the system is in a changed state: downstream nodes are told that the reference is no longer PRTC traceable, switch behavior, and later use the new path once it has been selected.
- Some chain-context signals, such as path-trace or reference-ID propagation, do have their own forwarding and convergence behavior.

The key distinction is that those richer chain-context signals are **not** the same thing as the archive's current tiny `boundary_context` wrapper.

## Smallest lifetime rule that survives the pressure

The current best rule is:

> `boundary_context` should piggyback on the lifetime of the local assessed state it explains.

Operationally this means:
- when the accompanying local assessed state is replaced, recomputed, or expires, its `boundary_context` expires with it
- a new state may attach a new `boundary_context`
- the archive does **not** add an independent timer or retention ladder for the current wrapper

## Why this is enough for now

### 1. The wrapper explains the current state transition
`boundary_context` is not an archive-wide event log.
It is the smallest explanation for how the current state was boundary-handled.
If the current state changes, the old wrapper is usually no longer the right explanation.

### 2. Separate expiry would overfit the current wrapper
The current wrapper contains only:
- `action`
- optional `reason`

That is too little structure to justify a second lifetime mechanism of its own.
The archive would be building retention machinery around a two-field object.

### 3. The pressure for independent lifetime belongs elsewhere
Path-trace and loop-detection style signals may need their own forwarding or freshness semantics.
But those are better treated as future chain-context surfaces,
not as reasons to enlarge `boundary_context` prematurely.

## Traceability case

If a boundary reports that traceability was downgraded or became unknown,
that explanation should stay attached while the downgraded state remains current.
Once a new path or new assessed state restores a different condition,
the old explanation should disappear with the old state unless a profile separately keeps history.

## Sync-dimension case

If a boundary reports reconfiguration or conflict around synchronization dimension,
that explanation should likewise stay only as long as the resulting assessed state remains the one in force.
A later stable state should carry its own explanation or none.

## Current archive judgment

No separate expiry rule is justified yet.

Current default:
- `boundary_context` is state-coupled
- it expires with the local assessed state it accompanies
- richer chain-context signals remain out of scope for this wrapper

## What this still does **not** settle

This note still does not decide:
- whether some profiles should export `boundary_context` by default or only on request
- whether a future chain-context surface needs freshness or hop-limited semantics
- whether historical retention belongs in logs or an operator plane rather than in runtime state

## Next useful move

Test whether `boundary_context` should be export-default, requestable, or local-only.
That is now the smallest remaining placement question for the wrapper.
