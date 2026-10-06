# Orthogonal persistence lesson: checkpointable systems make “recovery” a normal path

DeriveBSD already aims for:
- immutable artifacts
- atomic switching
- rollbackability
- receipts as the unit of explainability

Orthogonally persistent systems (EROS, CapROS, Grasshopper) push a related idea:
**persistence is not a special case.**
Objects and (sometimes) processes live across reboots without requiring “save/restore” APIs.

We do *not* need to make DeriveBSD an orthogonally persistent OS.
But the persistence literature contains a few high-leverage lessons for a system that treats state as a first-class contract.

## Lesson 1: checkpointing discipline beats ad-hoc recovery

Orthogonally persistent designs treat recovery as:
- periodic, consistent checkpoints
- replayable logs
- well-defined object identities

DeriveBSD already has the building blocks (ZFS snapshots, typed event logs, state datasets).
The tightening move is to make “checkpoint boundaries” explicit for critical subsystems.

**DeriveBSD mapping:**
- every privileged broker has an explicit state dataset + schema
- schema migrations are plans/receipts
- checkpoints are named artifacts (digest-bound snapshots)

See: `docs/217-state-datasets-and-migrations-as-evidence.md`, `docs/215-structured-event-log-as-evidence.md`.

## Lesson 2: stable identities are a feature (and an attack surface)

Persistent systems highlight a subtlety: if references survive across time, revocation and rotation must be designed in.

**DeriveBSD mapping:**
- prefer revocable indirections (leases, bookmarks)
- treat long-lived references as policy-governed objects

See: `docs/182-capability-leases-and-revocation.md`, `docs/198-persistent-file-capabilities-bookmarks.md`.

## Lesson 3: persistence wants resource accountability

Persistence mechanisms need:
- bounded retention
- GC policies
- explicit “what is pinned and why?”

DeriveBSD can keep this simple by reusing existing concepts:
- evidence retention budgets
- pin receipts
- explicit export/transparency entries for off-host persistence

See: `docs/246-causality-graphs-and-minimal-evidence-bundles.md`, `docs/254-export-transparency-logs.md`.

## References

- CapROS overview (orthogonal persistence + capabilities): https://www.capros.org/overview.html
- “EROS: A fast capability system” (SOSP 1999 PDF mirror): https://sites.cs.ucsb.edu/~chris/teaching/cs290/doc/eros-sosp99.pdf
- “Design Evolution of the EROS Single-Level Store” (Shapiro, 2002): https://rcs.uwaterloo.ca/papers/sls.pdf
- “Grasshopper: An orthogonally persistent operating system” (Dearle et al.): https://archive.cs.st-andrews.ac.uk/gh/pub/gh-03.pdf

Last updated: 2026-02-27
