# Link and constellation-join interface spec

The archive already has link groups, constellation records, member classes, claim objects, preflight reports, and replacement workflows.
This document answers the narrower practical question those abstractions still left open:

> what must a real device-join review surface literally show before apply, so AnonSync does not drift back into `link device` ritual?

This is the join-side companion to `66-claim-and-adoption-intake-interface-spec.md` and the identity/authority companion to `65-exit-review-and-replacement-interface-spec.md`.

## Why this needs its own spec

Resilio's docs are strong enough to make the problem unusually clear.
Linked devices make all folders visible and accessible across the linked set.
Linking one already-configured device to another can cause the new one to take the other device's identity name and fingerprint and receive its configured shares.
Remote users may choose to auto-approve all linked devices for future sharing after approving one.
Custom placement of linked folders depends on switching the whole target device into `Disconnected` mode and later clicking `Connect` share by share.
Linux uses WebUI as the default and only interface class, while at least one destructive-action safety preference is explicitly ignored in Linux WebUI.

The lesson is not that Resilio has no value.
The lesson is that a useful product can still compress too much meaning into one convenience gesture.

AnonSync should therefore make these differences explicit before apply:

- this device keeps its identity vs takes over another identity
- this device joins a constellation vs enters replacement/migration
- these shares become visible here vs nothing becomes visible yet
- this join widens local convenience only vs also widens approval or stewardship reach
- these defaults will govern later incoming shares on this member

## Core rule

A non-trivial device-join flow should always compile to a reviewed join surface.
That includes at least:

- adding a fresh device to an existing personal constellation
- linking an already-initialized device that already has identity or share state
- any join that changes member class, default visibility, or approval reach
- any join with compatibility, migration, release-family, or channel-parity warnings
- any join whose immediate visibility delta is large enough that a bare success banner would hide scope

A channel may compress the review when risk is truly low.
It may not replace the meaning with a vague `Link device` action.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench review card
- constellation page `Add member` action
- portable invite inspection sheet
- CLI `claim prepare --invite ... --group ... --member-class ...`
- TUI review lane entry

But these must all converge on the same public join model.
The operator should never have to wonder whether one surface is doing ordinary relationship add while another is really performing migration, identity takeover, or authority widening.

## Fixed review order

Every non-trivial join review should render the same sections in the same order:

1. **Identity and continuity**
2. **Membership and defaults**
3. **Visibility delta**
4. **Authority delta**
5. **Compatibility and migration**
6. **Receipt promise**

### 1) Identity and continuity

This section should show:

- candidate device identity, fingerprint, and stable handle
- whether the candidate keeps its current identity
- whether the proposed action is ordinary join, migration, replacement, or blocked takeover
- whether any state-root or service-profile clue suggests this is not a fresh device
- whether the action would consume or supersede any prior continuity intent

The operator must be able to answer: **is this device joining safely, or is something identity-sensitive happening?**

### 2) Membership and defaults

This section should show:

- target constellation / linked-group
- requested member class
- default visibility posture for future incoming shares
- default role or template where applicable
- approver-scope and successor-scope defaults that come with this membership

The operator must be able to answer: **what kind of member is this about to become?**

### 3) Visibility delta

This section should show:

- how many shares or incoming items become visible immediately
- whether they land as `incoming`, `detached`, `metadata-only`, `selective`, or some other reviewed posture
- whether any broad visibility policy, tag rule, or default profile caused that expansion
- whether any high-signal shares remain intentionally hidden on this member

The operator must be able to answer: **what becomes newly visible here right away?**

### 4) Authority delta

This section should show:

- whether the new member may mutate data
- whether it may re-share, revoke, approve future claims, or authorize successor action
- whether the join changes only visibility/default posture or also widens stewardship reach
- whether any linked-group or approval-memory rule is participating

The operator must be able to answer: **did this join only add convenience, or did it also widen trust?**

### 5) Compatibility and migration

This section should show:

- release-family and capability mismatches
- member-class incompatibilities
- channel-parity issues that would weaken safety-critical review on this member
- migration or replacement blockers if existing state suggests the wrong workflow
- whether apply is `ok`, `warning`, or `blocked`

The operator must be able to answer: **what would make this join unsafe or dishonest right now?**

### 6) Receipt promise

This section should show:

- which receipt will exist after apply
- what it will later prove about identity continuity, member class, visibility delta, and authority delta
- whether the receipt proves only membership change or also authority/default changes
- what remains inspectable after the invite or pending review entry disappears

The operator must be able to answer: **what later evidence will prove what this join actually changed?**

## Action hierarchy inside join review

The primary action should be the safest meaningful next step.
Examples:

- mixed-version or mixed-capability candidate → `Review blockers` or `Prepare migration`, not `Link anyway`
- existing-state candidate that looks like replacement → `Prepare replacement`, not `Join as member`
- low-risk fresh device with narrow defaults → `Prepare join` or `Apply join` may be primary

Destructive or confusing alternatives such as `Take over identity`, `Widen approvals`, or `Migrate now` should be visually separate and usually plan-bearing.

## What the surface must never imply

The join surface must never imply that these are the same thing:

- pairing a device vs migrating or replacing it
- joining a constellation vs receiving owner-like power
- making shares visible here vs mounting them here
- keeping local identity vs adopting another device's identity
- adding one member vs broadening future approvals across many members

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## Linux/WebUI parity rule

A Linux-first product has to assume that WebUI, TUI, CLI, and headless automation are not edge cases.
So the reviewed join grammar must survive across those channels.
It is not acceptable for a richer desktop client to show identity continuity and approval blast radius while Linux/WebUI falls back to a generic `Link device` success path.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync claim show <id> --view review` for link-target claims.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether a candidate device keeps its identity, what class it joins under, and what visibility/authority blast radius apply would create.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed join grammar is how the archive avoids rebuilding a system where linking is individually scriptable and individually convenient, yet the full meaning of the action still depends on which `Link device` prompt happened to appear first.
