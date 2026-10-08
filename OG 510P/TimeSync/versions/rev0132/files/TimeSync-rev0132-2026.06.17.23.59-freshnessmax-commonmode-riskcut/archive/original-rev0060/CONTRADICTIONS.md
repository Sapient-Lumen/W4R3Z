# CONTRADICTIONS

## CX-0001 — protocol vs system
TimeSync remains protocol-adjacent, but the stronger pattern still points to system-level and control-surface concerns.

## CX-0002 — global vs local
A global timing substrate may be the aspiration, but degraded local operation keeps appearing as part of the core problem.

## CX-0003 — practical vs ideal
The integration and greenfield tracks are both necessary, but the archive still lacks a decisive criterion for where they should merge or stay separate.

## CX-0004 — minimality vs usefulness
A smaller core is better only if it still carries enough signal for real downstream use.

## CX-0005 — time vs time/phase/frequency
Some pressure scenarios are really about phase and frequency synchronization as well as time.
The archive currently treats those as hook- and profile-level extensions.

## CX-0006 — TimeState vs broader state object
`sync_dimension` now looks like the clearest sign that a future redesign might need a broader state object than `TimeState`, but the archive does not yet have enough pressure to commit to that move.

## CX-0007 — broader object clarity vs archive discipline
A broader object may become necessary, but the archive must resist promoting a sketch into a real redesign before it has earned clear fields, semantics, and pressure cases.

## CX-0008 — global ranking vs profile-sensitive ranking
The archive now has evidence that some demanding P4 cases are frequency-first even though the archive overall still leans phase-first.
It must decide whether the first-missing-field question is fundamentally global or profile-sensitive.
