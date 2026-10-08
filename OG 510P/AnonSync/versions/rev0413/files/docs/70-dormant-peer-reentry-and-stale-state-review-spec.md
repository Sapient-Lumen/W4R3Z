# Dormant-peer re-entry and stale-state review interface spec

The archive already has settlement barriers, rollback provenance, compromise cases, and successor cutover.
This document answers the narrower practical question those abstractions still left open:

> what must a real stale-return surface literally show before apply, so AnonSync does not drift back into peer counters, invalid-time warnings, archive aftermath, and hide/reappear ritual?

This is the stale-return companion to `47-settlement-barrier-and-readiness-spec.md`, the replay-risk companion to `48-history-conflict-and-rollback-provenance-spec.md`, and the suspicious-reappearance companion to `69-compromise-containment-and-trust-rotation-interface-spec.md`.

## Why this needs its own spec

Resilio's docs are strong enough to make the problem unusually clear.
`How to clear offline devices?` says clearing only hides an offline device and that if it comes back online it will reappear and continue sharing as before.
`Sync Main View (Desktop)` says peer counts include offline peers and that a peer is only disconnected from a folder after 7 days offline, with the threshold configurable in power-user settings.
`What if several people make changes to the same file?` says an offline peer's later return can make its version override changes proposed earlier by online peers, with overwritten versions then moved to Archive.
`"Time difference" error` says recency depends on modification-time comparison converted to GMT and that more than 600 seconds of drift produces warnings; on mobile the result can be an empty file list.
`Cannot download files / ... no source peers online for too long time` then adds a separate “ghost file” condition where announcements outlived the real source bytes.

The lesson is not that Resilio has no value.
The lesson is that a useful product can still scatter stale-return meaning across too many clues.

AnonSync should therefore make these differences explicit before apply:

- this subject is merely visible again vs is requesting writable replay authority
- chronology is trustworthy vs guarded vs blocked
- announced bytes still exist vs only placeholder lore remains
- this is harmless dormancy vs suspicious reappearance vs successor/cutover drift
- the safest next action is resume, downgrade, quarantine, merge review, or containment escalation

## Core rule

A non-trivial stale return should always compile to a reviewed re-entry surface.
That includes at least:

- a device or share member returning after dormancy beyond the normal confidence window
- a subject whose modification-time or timezone evidence makes recency claims unreliable
- a returning subject whose announcements outlive actual source bytes
- a hidden-only subject reappearing in a way that may still carry real authority
- any stale return that could actually be compromise, replacement, or wrong-workflow drift instead of benign reconnection

A channel may compress the review when risk is truly low.
It may not replace the meaning with vague `online`, `resume syncing`, `hide again`, `conflict happened`, or `ignore warning` success language.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench report shelf `Open re-entry case`
- device detail `Review return`
- share detail `Review stale writer return`
- settlement or rollback report `Open stale return review`
- CLI `reentry open --subject ... --plan`
- CLI `device resume --plan` or `share admit-return --plan` when the operator-visible meaning is stale return handling
- compromise or successor surfaces when re-entry is detected as suspicious or continuity-sensitive

But these must all converge on the same public re-entry model.
The operator should never have to wonder whether one surface is only acknowledging visibility while another is actually restoring writable replay authority.

## Fixed review order

Every non-trivial stale-return review should render the same sections in the same order:

1. **Subject and dormancy**
2. **Chronology and evidence**
3. **Authority and scope**
4. **Divergence and availability**
5. **Admissible actions**
6. **Receipt promise**

### 1) Subject and dormancy

This section should show:

- which device, member, or subject is returning
- last-seen time and dormancy duration
- prior posture (`active`, `hidden-only`, `retired`, `quarantined`, `unknown`)
- related shares, grants, or sessions that make the return meaningful
- whether the subject had already been marked for exit, replacement, or containment

The operator must be able to answer: **what came back, after how long, and in what prior posture?**

### 2) Chronology and evidence

This section should show:

- clock or timezone confidence
- freshness of scan/index evidence
- whether chronology claims are `high`, `guarded`, `low`, or `blocked`
- what quorum, witness, or quiet-window evidence exists
- whether archive/conflict history already proves stale replay happened before review

The operator must be able to answer: **can I trust this subject's recency claims enough to let it replay state?**

### 3) Authority and scope

This section should show:

- what authority the subject would regain if resumed now
- whether the proposed posture is writer, reader, quarantined observer, successor-only, or blocked
- which shares or grants are affected
- whether any approvals, direct-path trust, or future introductions remain frozen
- whether the action should really divert into successor cutover or compromise handling instead

The operator must be able to answer: **what would this subject be allowed to do if I let it back in now?**

### 4) Divergence and availability

This section should show:

- offline-local changes detected on the returning subject
- remote changes made while it was absent
- pathname or capability collisions that need merge review
- announcements whose source bytes are no longer available
- whether any divergence is already resolved, still hypothetical, or actually blocked

The operator must be able to answer: **what disagrees, and are the claimed bytes even real?**

### 5) Admissible actions

This section should show:

- guarded resume options
- downgrade-to-reader or quarantine options
- merge-review or rollback-review options
- escalation into compromise containment or successor cutover
- why some tempting action is blocked or deliberately absent

The operator must be able to answer: **what safe choices are actually available from here?**

### 6) Receipt promise

This section should show:

- which receipt will exist after apply
- what it will later prove about dormancy, chronology confidence, authority outcome, divergence posture, and escalations
- whether the receipt remains provisional because fresh observation is still pending
- what later audit survives after the transient warnings are gone

The operator must be able to answer: **what later evidence will prove how this stale return was handled?**

## Action hierarchy inside re-entry review

The primary action should be the safest meaningful next step.
Examples:

- long-offline return with strong clock drift and active grants → `Quarantine subject` or `Resume as reader`, not `Resume syncing`
- low-risk laptop wake with fresh chronology proof and no divergence → `Apply guarded resume` may be primary
- return that looks like a replacement artifact or identity confusion → `Open successor comparison`, not `Resume device`

Confusing alternatives such as `Hide again`, `Ignore warning`, or `Open conflicts folder` should be visually separate and usually not primary.

## What the surface must never imply

The re-entry surface must never imply that these are the same thing:

- becoming visible again vs resuming writable replay authority
- acceptable dormancy vs suspicious reappearance
- chronology warning vs merge-ready replay
- archive after-the-fact preservation vs safe pre-apply admission
- a benign returning device vs a successor/cutover or compromise problem in disguise

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## Linux/WebUI parity rule

A Linux-first product has to assume that WebUI, TUI, CLI, and headless automation are not edge cases.
So the reviewed re-entry grammar must survive across those channels.
It is not acceptable for one richer surface to show dormancy, chronology, and replay-authority truth while Linux/WebUI falls back to peer counts and generic reconnect success.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync reentry show <id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether a returning subject is safe to trust, safe only to resume read-only, or should be quarantined or escalated.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed re-entry grammar is how the archive avoids rebuilding a system where dormancy, chronology, archive preservation, and conflict handling are individually scriptable and individually documented, yet the full meaning of “this thing came back” still depends on which status row, time warning, or archive artifact the operator happened to notice first.
