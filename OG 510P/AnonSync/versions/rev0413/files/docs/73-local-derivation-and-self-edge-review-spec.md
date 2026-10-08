# Local-derivation and self-edge review spec

The archive already has mount binding, namespace projection, storage pressure, filesystem fidelity, claim review, and conflict adjudication.
This document answers the narrower practical question those abstractions still left open:

> what must a real same-host derivation surface literally show before an operator fans one share into another local target, so AnonSync does not drift back into “sync local folders” convenience that hides loop risk, inherited authority, target-tier drift, and source-coupled lifecycle?

This is the same-host companion to `43-mount-binding-repair-and-preservation-spec.md`, the local-materialization companion to `46-namespace-projection-and-placeholder-spec.md`, the target-tier companion to `49-filesystem-portability-and-semantic-fidelity-spec.md`, and the textual-parity companion to `39-interface-pattern-language.md`.

## Why this needs its own spec

Resilio's docs make the seam unusually clear.
`Sharing a folder locally` says a local share can sync one folder to other folders on the same computer, can target USB and network paths, and connects only to one peer: self.
The same article warns not to choose a subdirectory or parent of the source because that creates syncing loops.
It also says local shares inherit source permissions, cannot receive `Owner`, can require remove-and-re-share ritual to change access in Advanced shares, are downgraded automatically when the source permission is downgraded, are removed when the source is disconnected or removed, do not automatically reconnect when the source later returns, cannot be locally re-shared again, and only receive data from the source share—so placeholder-only source state can leave the derived target without the file.

The lesson is not that same-host derivation is bad.
The lesson is that a useful product can still compress too many decisions into one convenience action.

AnonSync should therefore make these differences explicit before apply:

- local derivation vs export vs cache branch vs blocked loop
- source authority inheritance vs target-local mutability
- local-native target vs warning-tier USB/network target
- source-coupled lifecycle vs independently retained target
- placeholder/materialization dependence vs target availability promise
- one derived target vs reviewed fanout set

## Core rule

A non-trivial same-host derivation should always compile to a reviewed local-derivation surface.
That includes at least:

- any target that is on warning-tier or degraded target classes
- any target relationship that could create a parent/child/overlap loop
- any derivation whose lifecycle is coupled strongly enough that source detach or permission downgrade changes the target outcome
- any derivation whose source is not fully materialized or whose target promise depends on later source availability
- any derivation whose authority or mutability story differs from the source in ways an operator could misread
- any derivation that fans one source into multiple local targets with different tiers or policies

A channel may compress the review when risk is truly low.
It may not replace the meaning with vague `sync local folders`, `create mirror`, or `connect here too` prose.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench share detail `Create local derivative`
- target-path browser `Adopt as derived target`
- storage or fidelity report `Review local derivation`
- CLI `derive local create --from <share> --to <path> --plan`
- CLI `derive local show <id> --view review`

But these must all converge on the same public local-derivation model.
The operator should never have to wonder whether one surface is merely asking for a path while another is actually explaining topology risk, lifecycle coupling, and target-tier truth.

## Fixed review order

Every non-trivial local-derivation review should render the same sections in the same order:

1. **Source and target**
2. **Topology and loop risk**
3. **Authority and lifecycle coupling**
4. **Materialization and target-tier reality**
5. **Admissible derivations**
6. **Receipt promise**

### 1) Source and target

This section should show:

- which source share, mount, or projection is being derived
- the target path, host profile, and target tier
- whether the proposal is local-native, removable media, network-reviewed, or blocked
- whether the derivation is single-target or part of a reviewed fanout set

The operator must be able to answer: **what is being derived from what, and onto what kind of target?**

### 2) Topology and loop risk

This section should show:

- whether the target is disjoint, sibling, child, parent, overlapping, or ambiguous relative to the source
- whether recursive visibility, duplicate indexing, or path echo could occur
- whether the product can prove the relationship is loop-safe or only warning-tier safe
- whether existing derived targets already create a fanout pattern that changes the risk story

The operator must be able to answer: **could this arrangement feed back into itself, overlap dangerously, or create topology confusion later?**

### 3) Authority and lifecycle coupling

This section should show:

- which permissions, mutability, and delegation rights the derivative inherits
- whether the target can ever exceed source authority or only narrow it
- whether source detach, permission downgrade, or source retirement will remove, freeze, or merely detach the derivative
- whether target edits travel back to the source, remain local-only, or are blocked by policy

The operator must be able to answer: **who can change the derivative, and what happens to it when the source changes or disappears?**

### 4) Materialization and target-tier reality

This section should show:

- whether the source is fully materialized, placeholder-backed, metadata-only, or otherwise incomplete for the target promise
- whether the derivative promises mirrored bytes, on-demand bytes, cache-only bytes, or review-blocked bytes
- whether the target tier weakens fidelity, durability, or observation guarantees
- whether a removable or network-reviewed target changes archive/history expectations

The operator must be able to answer: **will this target really have the bytes and semantics I think it will, on this tier, under these source conditions?**

### 5) Admissible derivations

This section should show:

- create read-only derivative
- create writable derivative when topology and authority make that honest
- create cache/materialized branch with explicit byte promise
- narrow to safer target tier or safer lifecycle coupling
- reject or defer because the topology or target class is unsafe

The operator must be able to answer: **what safe same-host derivation choices are actually available here?**

### 6) Receipt promise

This section should show:

- which derivation receipt will exist after apply or reject
- what it will later prove about source, target, topology posture, inherited authority, lifecycle coupling, and target-tier promise
- whether the receipt remains provisional because source materialization or target fidelity is weak
- what later audit survives after the derivation is already active

The operator must be able to answer: **what later evidence will prove how this derivative was created and what promises it actually made?**

## Action hierarchy inside local-derivation review

The primary action should be the safest meaningful next step.
Examples:

- target path is a child of the source → `Reject as loop risk`, not `Create writable derivative`
- source is placeholder-heavy and target promise implies durable offline bytes → `Create cache/materialized branch` or `Block until materialized`, not `Create ordinary derivative`
- target tier is network-reviewed and lifecycle coupling is surprising → `Narrow to read-only derivative` or `Pick stronger target`, not `Create mirror`

Convenience labels such as `Sync local folders`, `Mirror here`, or `Connect target` should be visually separate and usually not primary.

## What the surface must never imply

The local-derivation surface must never imply that these are the same thing:

- same-host derivation vs remote share adoption
- target-path choice vs target-tier trustworthiness
- inherited authority vs target-local mutability
- source detach vs derivative independence
- placeholder visibility vs durable local byte availability
- multi-target fanout vs one-off local export

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## Linux/WebUI parity rule

A Linux-first product has to assume that WebUI, TUI, CLI, and headless automation are not edge cases.
So the reviewed local-derivation grammar must survive across those channels.
It is not acceptable for one richer surface to show topology, lifecycle, and target-tier truth while Linux/WebUI falls back to a path picker plus a `Create local copy` button.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync derive local show <id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether the target is loop-safe, whether it inherits writable authority, or whether source materialization and target tier weaken the promised outcome.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed local-derivation grammar is how the archive avoids rebuilding a system where same-host fanout, removable targets, inherited authority, source-coupled lifecycle, and placeholder dependence are all individually documented, yet the full meaning of “what exactly am I creating on this machine, what happens if the source changes, and is this topology actually safe?” still depends on which menu, warning, or support article the operator happened to notice first.
