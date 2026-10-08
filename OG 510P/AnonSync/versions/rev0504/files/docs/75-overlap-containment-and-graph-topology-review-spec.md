# Overlap, containment, and graph-topology review spec

The archive already has mount binding, local derivation, filesystem fidelity, authority mutation, and claim review.
This document answers the narrower practical question those abstractions still left open:

> what must a real topology surface literally show before an operator nests one share inside another, moves a bound path across graph boundaries, or accepts an overlap that changes propagation shape, so AnonSync does not drift back into child-share caveats, loop warnings, and reconnect folklore?

This is the graph-topology companion to `43-mount-binding-repair-and-preservation-spec.md`, the overlap companion to `73-local-derivation-and-self-edge-review-spec.md`, the path-boundary companion to `49-filesystem-portability-and-semantic-fidelity-spec.md`, and the textual-parity companion to `39-interface-pattern-language.md`.

## Why this needs its own spec

Resilio's docs make the seam unusually clear.
`Is it possible to share a nested folder separately?` says a parent and child folder can both be shared, but only if both have Read & Write or Owner permissions, both disable Selective Sync, the child is indexed and rescanned separately in addition to as part of the parent, peers with only the parent do not seed peers that only have the child, and child edits still reach parent-share peers through the parent topology.
`Sharing a folder locally` separately warns not to choose a subdirectory or parent of the source because that creates syncing loops.
`Can I move or rename a syncing folder?` says rename is local-only, Windows/macOS moves are limited to the same drive, Linux moves are limited to within the Sync parent folder, and otherwise the operator falls back to disconnect/reconnect-style repair.
`Running Sync in configuration mode` adds `directory_root_policy`, `dir_whitelist`, and the rule that configured shares disable WebUI.

The lesson is not that graph complexity is bad.
The lesson is that a useful product can still compress too many topology decisions into “add another folder”, “move it”, or “reconnect it here”.

AnonSync should therefore make these differences explicit before apply:

- disjoint graph subject vs child-inside-parent vs ambiguous overlap
- independent propagation vs piggyback-via-parent vs self-edge or blocked loop
- local-only rename vs reviewed rebind vs root-boundary escape
- allowed topology vs topology that disables selective/materialization options
- same-host derivation vs true separate share graph vs move across graph boundaries
- safe nesting vs strong enough blast radius that flattening or rejection is the more honest action

## Core rule

A non-trivial topology change should always compile to a reviewed topology surface.
That includes at least:

- any child-inside-parent or overlapping relation among shares, mounts, or candidate paths
- any path move whose continuity depends on rebind, disconnect/reconnect-like behavior, or changed root policy rather than ordinary local rename
- any graph relationship that changes propagation shape, indexing cost, or source/seed expectations
- any action whose current or requested path posture depends on configured allowed roots, whitelists, or other policy-root restrictions
- any action whose safest next step may actually be flattening, rebind review, filesystem-policy review, or rejection rather than ordinary bind/add

A channel may compress the review when risk is truly low.
It may not replace the meaning with vague `Add folder`, `Move`, `Reconnect`, or `Use this path` prose.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench bind page `Review topology`
- workbench nested-share warning `Explain overlap`
- workbench local-derivation or claim page `Topology changes if accepted`
- CLI `topology review --subject ... --intent ... --plan`
- CLI `topology show <topology_case_id> --view review`
- CLI `bind repair --plan` when the real action changes graph relation rather than only restoring the same path

But these must all converge on the same public topology model.
The operator should never have to wonder whether one surface is merely picking a path while another is actually explaining double indexing, propagation shape, and root-boundary fallout.

## Fixed review order

Every non-trivial topology review should render the same sections in the same order:

1. **Trigger and graph subjects**
2. **Containment and propagation shape**
3. **Path and root-boundary effects**
4. **Admissible topology actions**
5. **Receipt promise**

### 1) Trigger and graph subjects

This section should show:

- which share, mount, candidate path, or existing graph subjects are involved
- whether the requested action is nest, flatten, rebind, move-across-boundary, or reject-overlap
- which existing graph relation currently holds and what relation is being requested
- whether the action was initiated directly, by repair workflow, by derivation workflow, or by policy-root warning

The operator must be able to answer: **what objects are actually being related or moved here, and what graph change is being requested?**

### 2) Containment and propagation shape

This section should show:

- whether the relation is disjoint, child, parent, overlap, self-edge, or ambiguous
- whether propagation would be independent, piggyback through a parent, double-indexed, re-download-likely after move, or blocked
- whether Selective Sync, placeholder posture, or other materialization behavior becomes disabled or constrained under this relation
- whether indexing cost, replay shape, or seed expectations change enough to matter operationally

The operator must be able to answer: **how will changes actually flow through this graph if I accept it?**

### 3) Path and root-boundary effects

This section should show:

- whether the path transition is a local-only rename, reviewed rebind, disconnect/reconnect-like continuity break, or blocked move
- whether the path remains inside allowed root, needs reviewed root expansion, or violates current root policy
- whether any surface loses expressive power because the requested topology exists only in config or only with reduced UI support
- whether the right next step is continue here, choose another path, expand root policy, or abandon the requested topology

The operator must be able to answer: **is this path transition really safe and supported, on this root policy and on this channel?**

### 4) Admissible topology actions

This section should show:

- accept reviewed nested topology
- flatten by keeping only parent or only child graph subject
- rebind outside the conflicting parent graph
- reject overlap or self-edge
- review root expansion separately before proceeding
- divert into local-derivation, bind repair, or filesystem-policy review when ordinary topology acceptance is not the honest frame

The operator must be able to answer: **what safe graph actions are actually available here?**

### 5) Receipt promise

This section should show:

- which topology receipt will exist after apply or reject
- what it will later prove about accepted graph relation, propagation shape, path/root-boundary findings, and any remaining follow-up review
- whether the receipt remains provisional because some related subject was offline or root policy was only partially changed
- what later audit survives after the topology is already active

The operator must be able to answer: **what later evidence will prove what graph relation I accepted, how it was expected to propagate, and what still needed follow-up?**

## Action hierarchy inside topology review

The primary action should be the safest meaningful next step.
Examples:

- candidate child path sits inside an existing broader share → `Review nested topology`, not `Add share`
- move would escape allowed root → `Review root expansion`, not `Reconnect here`
- overlap is ambiguous and propagation cannot be stated honestly → `Reject overlap`, not `Apply anyway`
- a safe disjoint sibling path is available → `Rebind outside parent graph`, not `Accept double-indexed child`

Convenience labels such as `Add folder`, `Move`, or `Reconnect` should be visually separate and usually not primary.

## What the surface must never imply

The topology surface must never imply that these are the same thing:

- child-inside-parent share vs ordinary disjoint second share
- same-host derivation vs separate replicated graph subject
- local-only rename vs reviewed rebind across graph boundaries
- allowed-root move vs root-boundary escape
- independent propagation vs piggyback-via-parent delivery
- nested acceptance vs loop-safe flattening

If the product compresses those differences, it has recreated the folklore it is trying to replace.

## Linux/WebUI parity rule

A Linux-first product has to assume that WebUI, TUI, CLI, and headless automation are not edge cases.
So the reviewed topology grammar must survive across those channels.
It is not acceptable for one richer surface to show graph relation, propagation shape, and root-boundary truth while Linux/WebUI falls back to a path picker plus generic `Apply` or `Reconnect` button.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync topology show <topology_case_id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether a child path is truly separate, whether a move becomes a reviewed rebind, whether propagation piggybacks through a parent, or whether the requested path actually violates current allowed-root policy.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed topology grammar is how the archive avoids rebuilding a system where nested-share caveats, local loop warnings, move limitations, allowed-root policy, and config-surface restrictions are all individually documented, yet the full meaning of “what graph did I just create, how will it propagate, and is this path transition actually safe?” still depends on which FAQ, warning, or support article the operator happened to notice first.
