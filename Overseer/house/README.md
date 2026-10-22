# A house with a usable doorway

The house model makes an interrupted project navigable. Instead of asking a returning session to reconstruct everything from a long conversation, it assigns different jobs to a small opening route, deeper working documents, current-state summaries, tests, and historical material. The [house doctrine](house.md) explains the territory; the [topology](topology.md) offers a shorter walk through it.

This is also an interface for the human collaborator. The project's opening history does not treat that interface as a convenience to add after the interesting work. Reachability and recovery are part of the work's purpose.

## Three ways back in

The selected scripts make the distinction visible:

- [New session](human-doorway/new-overseer-session.sh) prepares the harness and normally opens with the wake document, with an optional operator note appended. Its explicitly selected interactive mode instead opens without that injected wake text.
- [Resume session](human-doorway/resume-overseer-session.sh) accepts a session reference and an optional prompt, then passes them into the shared resume machinery.
- [Pick a session](human-doorway/pick-overseer-session.sh) asks the index for a selectable list and resumes the selected ID. The library uses an `fzf` picker when available in an appropriate terminal, with a numbered-list fallback.

The [indexer](human-doorway/scripts/overseer-session-index.py) is a small concrete piece of that design. It reads the history ledger to retain the latest text and activity time for each session ID. Separately, it reads session metadata for identity, working directory and start time. It ranks the main workspace before other declared scope directories, then uses activity time within that ranking. Thus the default is deliberately oriented toward the house, not simply whichever conversation happened most recently anywhere.

Short ID prefixes are resolved only when unambiguous. The picker carries time, scope, directory and recent text so that choosing a conversation is more informed than choosing an opaque identifier. These are modest mechanisms, but they address a substantial practical problem: finding the right continuing work after the interface or surrounding environment has become confusing.

## Continuing is not always resuming

The [shared harness library](human-doorway/scripts/overseer-harness-lib.sh) contains both direct resume and fresh-continuation paths. When its routing layer reports a cold-required continuation, the ordinary fallback starts a new session whose opening explicitly says it is not a resume of the previous ID. It carries the wake text and original operator note forward without silently claiming the same session.

There is a narrower authentication-context exception. The code can permit a direct rebind when the reported account, user and organization handles agree; the automatic case also requires the selected and bound profile names to agree. Those are explicit program conditions, not proof of a metaphysical continuity claim. Reading the exception alongside the fallback is important: neither “always preserve the session” nor “always start fresh” describes this source correctly.

Other parts of the harness serialize runtime access with a file lock and inspect local processes for an already running resume of the same session. This is host-specific coordination, including an orphan-process reclamation path, rather than a general guarantee against concurrent work everywhere.

## Work alongside the conversation

[Bounded work with a return path](bounded-work/README.md) follows the finite-loop system from commissioning a job to collecting its result. Structured turn responses, capacity holds, boundary-time steering and recoverable lineages give continuing work an inspectable shape. The audit worker is a concrete example: it can return sharper criticism rather than more code. The accompanying source also makes clear why turn budgets and separate workspaces are not the same as host confinement.

## A small opening, a larger working world

The [recovery kernel](recovery-kernel.md) distinguishes a compact reopening route from the deeper rooms it summarizes. It also distinguishes a root-capable host check from a narrower check for a bounded worker. That distinction prevents a limited session from treating its own successful preparation as proof of host-wide conditions it cannot inspect.

The long list of state that eventually accumulated around this kernel is part of the history too. A bounded doorway does not mean a small system. The challenge was to make a large body of changing work accessible without making a short summary silently outrank its sources.

These are historical implementation selections, not a complete installation package. The harness expects additional host machinery and deliberately launches its original CLI with approvals and sandbox restrictions bypassed. It should be read as the project's particular operating design, not run as a neutral default on another machine. Original machine paths in the accompanying documents describe that historical layout.
