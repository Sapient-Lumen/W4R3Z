# Conflict-adjudication and path-collision review spec

The archive already has conflict objects, rollback provenance, filesystem fidelity, stale-return review, and destructive-replay review.
This document answers the narrower practical question those abstractions still left open:

> what must a real conflict-adjudication surface literally show before an operator chooses a winner, loser handling, or deferral, so AnonSync does not drift back into magic suffixes, path folklore, and safe-removal ritual?

This is the conflict-decision companion to `48-history-conflict-and-rollback-provenance-spec.md`, the filesystem-fidelity companion to `49-filesystem-portability-and-semantic-fidelity-spec.md`, the intake-safety companion to `66-claim-and-adoption-intake-interface-spec.md`, and the textual-parity companion to `39-interface-pattern-language.md`.

## Why this needs its own spec

Resilio's docs are strong enough to make the problem unusually clear.
`Conflict files in Sync` says operators must not simply delete a `.Conflict` file or folder because that deletes the real remote counterpart, and its safe-removal recipe still tells them to move a healthy file out of the syncing tree, delete the conflict-named entries, and copy the healthy file back.
The same article shows conflict suffixes proliferating when folders are re-added or conflict files are renamed into new collisions.
`Power user preferences` adds more hidden semantics: `fix_conflicting_paths` can suppress conflict-file creation while leaving the share unsynced and “unpredictable”, while `normalize_unicode_paths`, `ignore_symlinks`, and `sync_max_time_diff` all shape whether the product treats a path problem as resolvable, delayed, or broken.

The lesson is not that Resilio has no conflict handling.
The lesson is that a useful product can still leave too much adjudication meaning spread across filename folklore, path caveats, and advanced toggles.

AnonSync should therefore make these differences explicit before resolve:

- content concurrency vs delete-vs-modify vs path/case/unicode/materialization collision
- local-only repair vs replicated winner selection vs blocked compatibility mismatch
- strong candidate evidence vs guarded authority/chronology posture
- safe loser preservation vs destructive loser handling
- ordinary defer-and-review vs escalation into portability, stale-return, or compromise workflows

## Core rule

A non-trivial conflict should always compile to a reviewed conflict-adjudication surface.
That includes at least:

- any delete-vs-modify conflict
- any case, unicode, symlink, placeholder/materialization, or path-mapping collision
- any conflict whose winning choice would replicate beyond the local subject
- any conflict where loser handling could destroy the only plainly recoverable local bytes
- any conflict whose candidate provenance, chronology, or authority posture is weak enough that the safest next action may be defer, narrow, or escalate rather than resolve now

A channel may compress the review when risk is truly low.
It may not replace the meaning with vague `keep both`, `delete the .Conflict file`, `re-add the folder`, or `overwrite changed files` success language.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench review card `Open conflict review`
- share detail `Review conflict`
- history/rollback card `Open adjudication`
- filesystem portability or stale-return report `Review collision`
- CLI `conflict show <id> --view review`
- CLI `conflict resolve <id> --winner ... --plan`
- CLI `conflict defer <id> --reason ...` when the operator-visible meaning is explicitly postponing adjudication

But these must all converge on the same public conflict-adjudication model.
The operator should never have to wonder whether one surface is merely showing filenames while another is actually explaining candidates, propagation, loser handling, and compatibility truth.

## Fixed review order

Every non-trivial conflict review should render the same sections in the same order:

1. **Trigger and semantic class**
2. **Candidates and authority posture**
3. **Path, materialization, and compatibility reality**
4. **Resolution scope and loser handling**
5. **Admissible resolutions**
6. **Receipt promise**

### 1) Trigger and semantic class

This section should show:

- which share, path set, and subject triggered the review
- whether the class is content concurrency, delete-vs-modify, case collision, unicode collision, path mapping, materialization mismatch, or capability mismatch
- when the conflict was detected and whether related stale-return, portability, or compromise findings already exist
- whether the product believes the conflict is ordinary collaborative churn, an adoption/cutover side effect, or suspicious unexpected replay

The operator must be able to answer: **what kind of conflict is this, where did it appear, and why is it being shown to me now?**

### 2) Candidates and authority posture

This section should show:

- the candidate versions or candidate path states
- which peer, device, or local subject each candidate came from
- modification time or chronology posture and whether it is `high`, `guarded`, `low`, or `blocked`
- whether any candidate is already policy-favored or policy-blocked
- whether the eventual winner would be local-only, replicated, or still subject to later settlement proof

The operator must be able to answer: **what are the real candidates here, who supplied them, and how much should I trust their claim to win?**

### 3) Path, materialization, and compatibility reality

This section should show:

- whether the conflict is fundamentally about bytes, names, case, unicode normalization, placeholder/materialization state, symlink/junction handling, or unsupported symbols
- which local filesystem tiers or portability findings constrain the decision
- whether any candidate cannot actually coexist or land cleanly on this target path
- whether a winner choice would still leave unresolved portability risk on other peers

The operator must be able to answer: **is this really a content choice, or is the filesystem/path model itself part of the problem?**

### 4) Resolution scope and loser handling

This section should show:

- whether the winning choice affects only this subject, the share, or a wider replicated scope
- what will happen to the losing candidate: left intact elsewhere, copied aside, quarantined, preserved in history, deleted locally, or deleted share-wide
- whether any preserved copy is the last easy recovery path
- whether the chosen resolution itself is destructive enough to require plan/apply or stronger witness

The operator must be able to answer: **if I pick this winner, what scope changes and what exactly happens to the loser?**

### 5) Admissible resolutions

This section should show:

- choose a winner with explicit loser handling
- preserve both under reviewed rename or copy-aside behavior
- defer with a reason and keep the conflict open
- divert into portability repair, stale-return review, or compromise review when the safest next action is not adjudication yet
- quarantine a candidate or narrow scope when ordinary replicated resolution would be too risky

The operator must be able to answer: **what safe choices are actually available from here?**

### 6) Receipt promise

This section should show:

- which rollback/conflict receipt will exist after resolution or defer
- what it will later prove about class, candidates, winner, loser handling, and scope
- whether the receipt remains provisional because chronology, portability, or settlement evidence is still weak
- what later audit survives after the visible conflict badge is gone

The operator must be able to answer: **what later evidence will prove how this conflict was handled?**

## Action hierarchy inside conflict review

The primary action should be the safest meaningful next step.
Examples:

- case/unicode/path collision on a warning-tier filesystem with unresolved portability drift → `Defer and open portability repair`, not `Choose winner`
- delete-vs-modify with weak chronology and a stale-returning writer → `Defer` or `Escalate to re-entry review`, not `Resolve now`
- ordinary content concurrency with strong candidate evidence and safe loser preservation → `Resolve conflict` may be primary

Confusing alternatives such as `Delete .Conflict`, `Re-add folder`, or `Keep whichever sync picked first` should be visually separate and usually not primary.

## What the surface must never imply

The conflict-adjudication surface must never imply that these are the same thing:

- conflict naming artifact vs actual semantic class
- local cleanup vs replicated winner selection
- preserved loser copy vs safe loser deletion
- content concurrency vs filesystem/path incompatibility
- after-the-fact rollback folklore vs explicit pre-resolution review

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## Linux/WebUI parity rule

A Linux-first product has to assume that WebUI, TUI, CLI, and headless automation are not edge cases.
So the reviewed conflict grammar must survive across those channels.
It is not acceptable for one richer surface to show class, candidates, compatibility reality, loser handling, and receipt truth while Linux/WebUI falls back to suffix filenames and a `Resolve` button with no reviewed scope story.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync conflict show <id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether a conflict is safe to resolve now, safe only to defer, or actually needs portability, re-entry, or compromise review first.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed conflict-adjudication grammar is how the archive avoids rebuilding a system where filenames, portability quirks, advanced toggles, and rollback history are individually documented, yet the full meaning of “which version should win here, on what scope, and what happens to the loser?” still depends on which suffix, warning, or support article the operator happened to notice first.
