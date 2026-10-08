# Pre-existing-material reconciliation and timestamp-authority spec

The archive already has claim/adoption intake, target custody, path comparison, conflict adjudication, and observer posture.
This document answers the narrower practical question those abstractions still left open:

> what must a real non-empty-target bind surface literally show before an operator adopts, repairs, or relocates a share into pre-existing material, so AnonSync does not drift back into `Folder not empty`, reconnect, or `latest timestamp wins` folklore?

This is the populated-target companion to `66-claim-and-adoption-intake-interface-spec.md`, the custody companion to `81-target-custody-and-exclusive-bind-review-spec.md`, and the conflict-decision companion to `72-conflict-adjudication-and-path-collision-review-spec.md`.

## Why this needs its own spec

Resilio's docs are strong enough to make the problem unusually clear.
`Folder not empty` says the warning appears both when adding into an existing folder and when reconnecting a folder that was syncing before, and that pre-existing files in the receiving folder may be deleted or overwritten.
`Can I connect two pre-populated pre-existing folders?` says Sync hashes both trees, skips identical files, merges other files, and lets the latest timestamp win when same-named files have different content.
`Disconnecting and Removing Folders` says reconnect can propose a different path, create a duplicate-index directory, and still tells the operator to ignore the non-empty warning when re-establishing the old directory.
`Encrypted folders` adds a materially different case: a non-empty target should not be used, because ordinary existing files are ignored, while bytes already encrypted with the same encrypted key can still be re-synced and moved to Archive.

The lesson is not that Resilio has no compare logic.
The lesson is that a useful product can still hide too many materially different outcomes behind one small confirmation step.

AnonSync should therefore make these differences explicit before apply:

- same-lineage reuse of a previously bound target
- harmless merge of identical plus local-only/remote-only material
- same-path divergence where chronology and authority both matter
- encrypted-target mismatch where existing bytes are not part of an ordinary plaintext merge story at all

## Core rule

A non-empty-target bind should always compile to a reviewed reconciliation surface when any of these are true:

- target lineage is ambiguous
- the target contains same-path divergent bytes
- the target is an encrypted/annex destination whose existing bytes are not plainly safe for reuse
- chronology confidence is weak enough that timestamp ordering is only guarded evidence
- local preservation or quarantine decisions could destroy the easiest remaining recovery path

A channel may compress the review when risk is truly low.
It may not replace the meaning with `Folder not empty`, `Add anyway`, `Reconnect`, or `latest timestamp wins` success language.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench compare card `Open reconciliation`
- incoming-share page `Reconcile target`
- mount repair page `Review reconciliation`
- CLI `incoming reconcile <id> --path ... --plan`
- CLI `mount reconcile <id> --path ... --plan`
- API-backed automation that prepares, shows, and applies reconciliation cases explicitly

But these must all converge on the same public reconciliation model.
The operator should never have to wonder whether one surface is merely showing compare counts while another is quietly deciding which bytes win.

## Fixed review order

Every non-trivial reconciliation review should render the same sections in the same order:

1. **Target lineage and operator intent**
2. **Compared material classes**
3. **Same-path divergent candidates and chronology posture**
4. **Admissible reconciliation actions**
5. **Preservation, quarantine, and annex effects**
6. **Receipt promise**

### 1) Target lineage and operator intent

This section should show:

- the triggering incoming share, mount, or repair target
- requested action (`adopt`, `repair`, `relocate`, `attach local derivative`, or similar)
- requested target path
- target-lineage posture (`same-lineage-likely`, `same-lineage-unproven`, `foreign-local-tree`, `encrypted-target-mismatch`, or similar)
- what evidence supports that lineage claim: prior receipts, custody markers, hash overlap, known subject state, or none

The operator must be able to answer: **am I reconnecting this share to its own old place, or aiming it at some other local tree that only happens to overlap?**

### 2) Compared material classes

This section should show:

- identical counts
- local-only counts
- remote-only counts
- same-path-divergent counts
- path-collision counts
- whether comparison freshness is still current enough for apply

The operator must be able to answer: **what merely merges, and what genuinely disagrees at the same path?**

### 3) Same-path divergent candidates and chronology posture

This section should show:

- the divergent paths or a reviewed summary when there are many
- candidate versions for each divergent path
- source and authority posture for each candidate
- chronology posture (`high`, `guarded`, `low`, or `blocked`)
- whether any ranking comes only from timestamp evidence

Timestamp freshness may still matter, but it should be presented as evidence quality, not as a hidden winner rule.
The operator must be able to answer: **if the product thinks one side is newer, how much should I trust that claim?**

### 4) Admissible reconciliation actions

This section should show:

- bind identical and remote-only material directly
- preserve local-only material while adopting the share
- choose an explicit winner for same-path divergent bytes
- quarantine or copy-aside local material first
- block and defer when chronology, lineage, or encrypted-target posture is too weak

The operator must be able to answer: **what safe choices are actually available from here, and which bytes do they affect?**

### 5) Preservation, quarantine, and annex effects

This section should show:

- whether local-only or losing bytes will be preserved, copied aside, quarantined, or replaced
- whether encrypted/annex targets require a different placement or a clean empty target
- whether any action would increase local archive/history cost materially
- whether a later restore path depends on preserving these bytes now

The operator must be able to answer: **what happens to the pre-existing local material if I proceed?**

### 6) Receipt promise

This section should show:

- which reconciliation receipt will exist after apply
- what it will later prove about lineage, compared classes, candidate handling, and preservation
- whether chronology or lineage confidence was strict or guarded
- what later audit survives after the warning or compare card is gone

The operator must be able to answer: **what later evidence will prove how this non-empty target was handled?**

## Special encrypted-target rule

Encrypted-target intake should never be treated as an ordinary non-empty plaintext merge.
If the target already contains unrelated plaintext or unrelated encrypted bytes, the product should block or divert into preservation-aware review.
If the target contains same-key encrypted bytes and reuse is supported, that should still render as explicit reuse with explicit archive/quarantine consequences.

## What the surface must never imply

The reconciliation surface must never imply that these are the same thing:

- same-lineage reuse vs foreign local-tree adoption
- local-only material vs same-path divergent material
- timestamp ranking vs trustworthy winner authority
- harmless merge vs reviewed replacement
- encrypted-target reuse vs ordinary plaintext bind

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync incoming reconcile <id> --path ... --view review` or `anonsync mount reconcile <id> --path ... --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether a non-empty target is safe to bind directly, safe only after explicit preservation, or not admissible at all.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed reconciliation grammar is how the archive avoids rebuilding a system where compare counts, target warnings, reconnect prompts, encrypted-target caveats, and timestamp winner rules are individually documented, yet the full meaning of “what exactly happens if I bind this share to that populated path?” still depends on which support article the operator happened to remember first.
