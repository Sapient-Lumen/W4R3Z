# Claim and adoption intake interface spec

The archive already has incoming-share objects, offer objects, claim objects, preflight reports, compare reports, and workbench review lanes.
This document answers the narrower practical question those abstractions still left open:

> what must a real way-in review surface literally show before apply, so AnonSync does not drift back into `Connect` ritual?

This is the intake-side companion to `65-exit-review-and-replacement-interface-spec.md`.

## Why this needs its own spec

Resilio's docs are strong enough to make the problem unusually clear.
Linking devices makes each new folder automatically available on all linked devices with full read-write access.
If a linked device is in `Selective Sync` or `Synced` mode, new folders land in the default folder.
Choosing a custom location requires switching that whole device into `Disconnected` mode first.
Reconnect docs then warn that reconnect may propose a different default path than the original one, may create a new directory there, and may add an index if a same-named folder already exists.
Separate pre-populated-folder docs tell the operator to click `Connect`, point at the existing directory, and explicitly accept the non-empty-folder warning.

The lesson is not that Resilio is incompetent.
The lesson is that a useful product can still leave too much acceptance meaning trapped in ritual.

AnonSync should therefore make these differences explicit before apply:

- visible here
- offered to this machine
- accepted locally on this machine
- mounted at this path
- authority widened beyond local adoption

## Core rule

A non-trivial way-in flow should always compile to a reviewed claim or adoption surface.
That includes at least:

- portable offer or invite acceptance
- linked incoming-share adoption
- incoming adoption into a non-empty path
- any acceptance that changes authority, not just local visibility
- any acceptance whose filesystem fit, fidelity, or path comparison is not obviously trivial

A channel may hide or inline the review when risk is truly low.
It may not replace the meaning with an ambiguous `Connect` verb.

## Entry points that must converge

The product may offer several ergonomic entry points:

- review card in the workbench
- share detail page for an incoming item
- portable-offer inspection sheet
- CLI `claim prepare` or `incoming adopt --plan`
- TUI review queue entry

But these must all converge on the same public intake model.
The operator should never have to wonder whether one surface is doing a local path bind while another is broadening trust.

## Fixed review order

Every non-trivial intake review should render the same sections in the same order:

1. **Source and offer**
2. **Local outcome**
3. **Path and filesystem**
4. **Authority delta**
5. **Blockers and drift**
6. **Receipt promise**

### 1) Source and offer

This section should show:

- source type (`incoming`, `offer`, `invite`, `replacement continuity`, or similar)
- source reference and stable IDs
- visibility origin (`manual-share`, `linked-policy`, `recovery`, etc.)
- who offered it or which policy surfaced it
- offered role/capability and whether claim review is mandatory
- peer pinning, expiry, redemption budget, and related constraints if present

The operator must be able to answer: **what became visible or was offered, and why?**

### 2) Local outcome

This section should show:

- target action (`link`, `grant`, `incoming-adopt`)
- requested linked group and member class when the target action is `link`
- requested local role or template
- requested materialization mode
- whether apply creates only incoming visibility, a mount, a grant, or several of these
- whether the outcome is deferred, draft-only, or ready to apply

The operator must be able to answer: **what exactly is this machine about to accept?**

### 3) Path and filesystem

This section should show:

- requested path or the fact that no path is yet selected
- path state (`missing`, `empty`, `non-empty`, `already bound`, `service-marker conflict`, etc.)
- referenced compare report when non-trivial
- referenced filesystem compatibility report and fidelity contract when non-trivial
- any downgrade, portability, case, normalization, symlink, or metadata warnings

The operator must be able to answer: **where will this land, and is that target actually safe?**

### 4) Authority delta

This section should show:

- whether local adoption also widens share authority
- whether re-share, approval, revoke, or owner-like power is being granted
- whether the action only changes local visibility or binding
- whether any linked-group, approval-memory, or defaults-profile implication is in play

The operator must be able to answer: **did this just mount something locally, or did it also widen trust?**

### 5) Blockers and drift

This section should show:

- compare blockers and collision classes
- stale-preflight or stale-claim drift
- incompatible policy or filesystem posture
- expiry, redemption-budget, or peer-pinning failures
- follow-up steps required before apply

This section should never be reduced to a generic warning banner if the action is otherwise complex.

### 6) Receipt promise

This section should show:

- which receipt will exist after apply
- what it will later prove
- whether the receipt proves only local outcome or also authority changes
- what remains inspectable after the original portable artifact or incoming state is gone

The operator must be able to answer: **what later evidence will prove what this machine accepted?**

## Action hierarchy inside intake

The primary action should be the safest real next step.
Examples:

- non-empty path with collisions → `Compare target` or `Refresh claim`, not `Adopt anyway`
- low-risk visible share with empty path → `Prepare claim` or `Adopt` may be primary
- portable offer with authority widening → `Inspect constraints` or `Prepare claim`, not `Open link`

Danger or rejection actions such as `Reject`, `Ignore source`, or `Quarantine` should be visually separated from ordinary adoption.

## What the surface must never imply

The intake surface must never imply that these are the same thing:

- seeing a share vs mounting it
- accepting a path vs widening share authority
- adopting one share vs changing device-wide defaults for future shares
- reusing an old path vs proving that the path is still safe

If the product compresses those differences, it has recreated the very ritual it is trying to replace.

## Linked-device convenience rule

Personal-device or constellation convenience is allowed to surface incoming items automatically.
It should not force the operator to change a whole-device mode just to place one share safely.
Per-share acceptance remains the public contract.

That means AnonSync should prefer:

- visible incoming items
- per-share claim preparation
- explicit path choice
- explicit compare/compatibility proof when needed

instead of a device-wide mode flip whose real purpose is only to make one later path-selection dialog behave safely.

## Portable-offer rule

Portable offers may arrive by file, URI, QR, clipboard, or local handoff.
The operator should still see one normalized intake review.
The delivery encoding should not change what the product says was offered or what the machine accepted.

## Cross-surface parity rule

GUI, WebUI, TUI, and CLI may differ in layout density.
They may not differ in:

- source truth
- accepted local outcome
- path/filesystem truth
- authority delta
- blocker truth
- receipt identity

If one surface renders those while another falls back to `Connect`, the product no longer has one trustworthy intake model.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync claim show <id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether a share is being mounted locally or whether authority is also expanding.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed intake grammar is how the archive avoids rebuilding a system where every important way-in decision is individually understandable, yet the full acceptance meaning still depends on which `Connect` prompt happened to appear first.
