# Authority-mutation and grant-boundary review spec

The archive already has grants, stewardship, constellation limits, cutover, compromise, local derivation, and claim review.
This document answers the narrower practical question those abstractions still left open:

> what must a real access-change surface literally show before an operator widens, narrows, freezes, revokes, or migrates live authority, so AnonSync does not drift back into folder-class ritual, owner folklore, and remove/re-share archaeology?

This is the grant-boundary companion to `61-personal-constellation-and-authority-domain-spec.md`, the stewardship companion to `30-interface-spec.md`, the dependent-fallout companion to `73-local-derivation-and-self-edge-review-spec.md`, and the textual-parity companion to `39-interface-pattern-language.md`.

## Why this needs its own spec

Resilio's docs make the seam unusually clear.
`What's the difference between Standard and Advanced folders?` says only Advanced folders support on-the-fly permission changes, only Owners can share Advanced folders with others, Standard folders can be re-shared by any peer who has the key it has, and Standard folders cannot be upgraded in place—they must be removed and re-added as Advanced.
`User Management` says live permission changes among Read Only, Read & Write, and Owner are available only for Advanced folders, linked same-identity devices all act as Owners, and `Disconnect` revokes future updates while leaving already-synced files in place.
`Sharing a folder locally` says a local share cannot receive `Owner`, changing local-share access for Advanced shares requires remove-and-re-share ritual, and source permission downgrades automatically flow down to the derivative.
`Running Sync in configuration mode` says config mode can set up only Standard folders, and if shared folders are set in the config file the WebUI is disabled.

The lesson is not that live permission changes are bad.
The lesson is that a useful product can still compress too many decisions into one dropdown or one overloaded action.

AnonSync should therefore make these differences explicit before apply:

- write authority vs delegation / re-share reach
- narrow access while preserving bytes vs revoke plus later cleanup
- direct mutation vs dependent fallout on local derivatives or linked members
- native grant model vs imported/legacy authority substrate that needs migration
- one subject change vs wider share-governance change that belongs in stewardship review
- safe local boundary tweak vs strong enough blast radius that cutover or compromise review is the better frame

## Core rule

A non-trivial authority mutation should always compile to a reviewed authority-mutation surface.
That includes at least:

- any widening from `ro` to `rw`, or from `rw` to any state with delegation or revoke power
- any narrowing that touches an active writer, a subject with dependent grants, or a subject with same-host derivatives whose mutability would change
- any action whose byte-retention consequence could be misread as erase, disconnect, or ordinary cleanup
- any action whose current or requested state depends on imported or legacy authority substrate rather than the native grant model
- any action whose safest next step may actually be stewardship review, successor cutover, or compromise containment rather than ordinary access editing

A channel may compress the review when risk is truly low.
It may not replace the meaning with vague `Change access`, `Disconnect`, `Make owner`, or `Re-share` prose.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench share member list `Change access`
- workbench review queue `Authority mutation pending`
- stewardship page `Narrow member authority`
- CLI `grant set <grant> --perm ... --plan`
- CLI `grant revoke <grant> --plan`
- CLI `grant show-mutation <plan_id> --view review`

But these must all converge on the same public authority-mutation model.
The operator should never have to wonder whether one surface is merely changing a label while another is actually explaining delegation loss, dependent fallout, and byte-retention consequences.

## Fixed review order

Every non-trivial authority-mutation review should render the same sections in the same order:

1. **Trigger and current authority**
2. **Desired boundary delta**
3. **Active subject state and coupled dependents**
4. **Authority-substrate and compatibility effects**
5. **Admissible mutations**
6. **Receipt promise**

### 1) Trigger and current authority

This section should show:

- which share, subject, and current grant or policy object is being changed
- current read, write, delegate, revoke, and approval reach
- whether the current state came from manual grant, policy inheritance, recovery carry-forward, or imported/legacy substrate
- whether the change was initiated directly, by stewardship policy, or by incident/cutover workflow

The operator must be able to answer: **what authority does this subject actually hold right now, and why?**

### 2) Desired boundary delta

This section should show:

- the requested post-change authority boundary
- whether the delta widens writes, narrows writes, strips delegation, freezes future updates, or revokes active reach entirely
- whether bytes already present remain intentionally in place, become local evidence only, or require a separate cleanup/reclaim action
- whether the requested result is smaller than, equal to, or wider than share-level caps and constellation caps

The operator must be able to answer: **what boundary is changing here, and what is deliberately not changing?**

### 3) Active subject state and coupled dependents

This section should show:

- whether the subject is currently writing, catching up, dormant, quarantined, or otherwise active
- whether local derivatives, linked members, dependent grants, approval memory, or other coupled subjects narrow automatically, remain unchanged, or become follow-up work
- whether any active settlement, destructive replay, or compromise state should block or strengthen the review
- whether the mutation is safe to apply now or should wait for stronger witness

The operator must be able to answer: **who else is affected, and what operational state makes this mutation safer or riskier right now?**

### 4) Authority-substrate and compatibility effects

This section should show:

- whether the current subject is already on the native grant model or still represented through imported/legacy authority substrate
- whether the requested state can be expressed directly or would force migration of authority substrate
- whether any channel or automation path lacks the expressive power to render the same decision honestly
- whether the right next step is mutate now, migrate first, or divert to stronger review

The operator must be able to answer: **can the system express the requested access boundary honestly, on this substrate and on this channel?**

### 5) Admissible mutations

This section should show:

- widen write without widening delegation
- narrow to read-only while preserving bytes
- strip delegation while keeping read/write as reviewed
- revoke future access while preserving currently present bytes
- divert into stewardship, cutover, or compromise review when ordinary mutation is not the honest frame
- reject because substrate migration or dependent fallout is still unresolved

The operator must be able to answer: **what safe authority changes are actually available here?**

### 6) Receipt promise

This section should show:

- which mutation receipt will exist after apply or reject
- what it will later prove about pre/post authority boundary, dependent fallout, preserved bytes, and any remaining follow-up review
- whether the receipt remains provisional because coupled subjects were offline or substrate migration was only partially completed
- what later audit survives after the mutation is already active

The operator must be able to answer: **what later evidence will prove what changed, what stayed, and what still needed follow-up?**

## Action hierarchy inside authority-mutation review

The primary action should be the safest meaningful next step.
Examples:

- subject is `rw` but should lose delegation only → `Strip delegation, keep writes`, not `Make read-only`
- subject is suspicious or stale-returning → `Divert to compromise/re-entry review`, not `Grant write`
- imported authority substrate cannot represent the requested result → `Review substrate migration`, not `Apply nearest available role`
- bytes should remain while future writes stop → `Narrow to read-only and preserve bytes`, not `Disconnect`

Convenience labels such as `Change access`, `Owner`, or `Disconnect` should be visually separate and usually not primary.

## What the surface must never imply

The authority-mutation surface must never imply that these are the same thing:

- write authority vs delegation / re-share reach
- revoke future access vs erase already-present bytes
- same-identity convenience vs owner-equivalent governance
- local-derivative fallout vs direct subject mutation
- imported/legacy substrate migration vs ordinary permission edit
- stewardship change vs one-subject access tweak

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## Linux/WebUI parity rule

A Linux-first product has to assume that WebUI, TUI, CLI, and headless automation are not edge cases.
So the reviewed authority-mutation grammar must survive across those channels.
It is not acceptable for one richer surface to show current authority, dependent fallout, and substrate migration truth while Linux/WebUI falls back to a dropdown plus a generic `Apply` or `Disconnect` button.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync grant show-mutation <plan_id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether a subject is losing only writes, also losing delegation, preserving bytes intentionally, or actually needs stronger review because the current authority substrate cannot represent the requested boundary honestly.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed authority-mutation grammar is how the archive avoids rebuilding a system where grants, stewardship, local derivation, same-identity convenience, disconnect actions, and imported authority substrate are all individually documented, yet the full meaning of “what exactly changes if I edit this subject's access right now, who else narrows with it, what bytes stay in place, and did I just widen owner-like power by accident?” still depends on which menu, folder class, or support article the operator happened to notice first.
