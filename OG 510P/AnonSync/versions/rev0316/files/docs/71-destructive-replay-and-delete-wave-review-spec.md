# Destructive-replay and delete-wave review interface spec

The archive already has file-intent scope, rollback provenance, activity phases, compromise handling, and stale-return review.
This document answers the narrower practical question those abstractions still left open:

> what must a real pre-apply destructive-review surface literally show before consent, so AnonSync does not drift back into pause semantics, archive toggles, overwrite checkboxes, and restore-after-the-fact ritual?

This is the destructive-propagation companion to `44-file-intent-deviation-and-restore-spec.md`, the consent companion to `48-history-conflict-and-rollback-provenance-spec.md`, the phase-truth companion to `45-activity-phase-and-scheduling-spec.md`, and the suspicious-wave companion to `69-compromise-containment-and-trust-rotation-interface-spec.md`.

## Why this needs its own spec

Resilio's docs are strong enough to make the problem unusually clear.
`How to pause syncing` says pause stops only downloads/uploads while deletions still sync and new files are still rescanned and indexed.
`Folder Preferences` says remote Read & Write changes and deletions are applied on other peers, with old copies moved to `.sync/Archive` by default for 30 days — but Archive can be disabled, in which case deleted files are no longer copied there.
The same preferences page says `Overwrite any changed files` for Read-Only folders is potentially destructive and disabled for Read-only folders with Selective Sync on.
`Is one-way synchronization possible?` adds more mode-dependent behavior: deleted files may be restored, edited files reverted, renamed files can be re-downloaded under the older name, while added files stay local and unsynced.

The lesson is not that Resilio has no value.
The lesson is that a useful product can still scatter destructive replay meaning across too many clues.

AnonSync should therefore make these differences explicit before apply:

- ordinary transfer pause vs actual destructive propagation freeze
- expected mirror maintenance vs suspicious delete/overwrite wave
- preserved copy exists vs recoverability is weak or absent
- destructive scope is narrow vs blast radius is large or touches protected paths
- the safest next action is apply, narrow, freeze, require stronger witness, or escalate

## Core rule

A non-trivial destructive replay should always compile to a reviewed destructive-replay surface.
That includes at least:

- a remote delete or overwrite wave above the normal confidence threshold
- destructive replay that touches protected, custody-tagged, or explicitly preserved local scope
- a receive-only, read-only, or revert-style action that would delete, restore-over, or re-download local state in non-obvious ways
- any destructive propagation where preservation posture is weak because history/versioning is disabled, expired, absent, or only partially witnessed
- any destructive wave whose contributing source set is stale-returning, chronology-uncertain, or suspicious enough that compromise or re-entry review may be the right next step

A channel may compress the review when risk is truly low.
It may not replace the meaning with vague `resume syncing`, `pause`, `archive enabled`, or `overwrite changed files` success language.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench report shelf `Open destructive replay review`
- share detail `Review delete wave`
- file-intent or rollback report `Open destructive review`
- receive-only / mirror deviation card `Review cluster revert`
- CLI `destructive open --share ... --plan`
- CLI `share admit-delete-wave --plan` or `file apply-remote --plan` when the operator-visible meaning is destructive replay consent
- compromise or stale-return surfaces when the delete wave is detected as suspicious or poorly witnessed

But these must all converge on the same public destructive-replay model.
The operator should never have to wonder whether one surface is merely pausing transfers while another is actually consenting to remote deletion or overwrite.

## Fixed review order

Every non-trivial destructive-replay review should render the same sections in the same order:

1. **Trigger and scope**
2. **Destructive effect summary**
3. **Preservation and recoverability**
4. **Authority and source confidence**
5. **Admissible actions**
6. **Receipt promise**

### 1) Trigger and scope

This section should show:

- which share, path set, or subject triggered the review
- whether the trigger is delete wave, overwrite wave, receive-only revert, protected-scope hit, or another destructive class
- the time window, peer set, and any protected-path or policy-scope involvement
- whether the action is routine maintenance, operator-requested, or unexpectedly observed
- whether related stale-return or compromise findings already exist

The operator must be able to answer: **what exactly triggered this review, where, and from whom?**

### 2) Destructive effect summary

This section should show:

- delete counts, overwrite counts, revert counts, or re-download counts as applicable
- approximate local-byte impact
- how much of the tree or which named subtrees are affected
- whether placeholder-only paths are involved versus fully materialized local bytes
- which effects are blocked already versus would occur immediately on apply

The operator must be able to answer: **what local state would actually be destroyed, replaced, or surrendered if I continue?**

### 3) Preservation and recoverability

This section should show:

- what rollback witness, archive, versioning, or preserved copy exists
- where that preserved copy exists and for how long
- which paths have weak, partial, or absent recoverability
- whether recoverability depends only on current local bytes still being present
- whether restore would itself require guarded or degraded readiness later

The operator must be able to answer: **if I accept this wave, what can I still recover later, and what would become unrecoverable?**

### 4) Authority and source confidence

This section should show:

- which peers or writers contributed the destructive state
- whether source confidence is `high`, `guarded`, `low`, or `blocked`
- whether chronology, readiness, or witness quality is degraded
- whether any contributing source is stale-returning, suspicious, or already under containment review
- whether this is ordinary share authority exercising expected policy or something that should escalate

The operator must be able to answer: **why should I trust this destructive wave at all?**

### 5) Admissible actions

This section should show:

- freeze destructive replay entirely
- allow only non-destructive sync progress
- require stronger witness and reopen review
- apply reviewed replay for all or only part of the scope
- escalate into compromise or stale-return review when the safest next step is not destructive apply

The operator must be able to answer: **what safe choices are actually available from here?**

### 6) Receipt promise

This section should show:

- which receipt will exist after apply or freeze
- what it will later prove about destructive scope, preservation posture, source confidence, and escalations
- whether the receipt remains provisional because witness collection or observation is still pending
- what later audit survives after the transient warnings are gone

The operator must be able to answer: **what later evidence will prove how this destructive wave was handled?**

## Action hierarchy inside destructive review

The primary action should be the safest meaningful next step.
Examples:

- large delete wave with weak preservation and a stale-returning writer → `Freeze destructive replay` or `Require stronger witness`, not `Apply replay`
- routine mirror cleanup with strong versioning, narrow scope, and trusted source set → `Apply reviewed replay` may be primary
- delete wave that looks like theft, wrong-machine edits, or suspicious remote behavior → `Escalate to compromise`, not `Pause syncing`

Confusing alternatives such as `Resume syncing`, `Archive will save you`, or `Open folder` should be visually separate and usually not primary.

## What the surface must never imply

The destructive-replay surface must never imply that these are the same thing:

- pausing transfers vs freezing destructive propagation
- having some archive/versioning vs having trustworthy recoverability for this wave
- read-only or receive-only revert behavior vs harmless cleanup
- local space reclaim vs replicated delete or overwrite consent
- after-the-fact restore folklore vs safe pre-apply destructive review

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## Linux/WebUI parity rule

A Linux-first product has to assume that WebUI, TUI, CLI, and headless automation are not edge cases.
So the reviewed destructive grammar must survive across those channels.
It is not acceptable for one richer surface to show trigger, blast radius, recoverability, and source-confidence truth while Linux/WebUI falls back to `Pause`, `Resume`, or an archive preference checkbox.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync destructive show <id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether a delete wave is safe to apply, safe only to narrow, or should be frozen or escalated.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed destructive-replay grammar is how the archive avoids rebuilding a system where pause, archive, versioning, and read-only behavior are individually scriptable and individually documented, yet the full meaning of “sync now wants to delete or overwrite a lot of local state” still depends on which setting, hidden folder, or troubleshooting article the operator happened to remember first.
