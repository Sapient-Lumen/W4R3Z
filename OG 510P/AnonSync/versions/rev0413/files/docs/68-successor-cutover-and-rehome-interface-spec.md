# Successor cutover and re-home interface spec

The archive already has recovery bundles, replacement workflows, state roots, service profiles, and reviewed exit language.
This document answers the narrower practical question those abstractions still left open:

> what must a real successor-cutover or continuity-sensitive re-home surface literally show before apply, so AnonSync does not drift back into installer, link, or migration ritual?

This is the continuity-side companion to `65-exit-review-and-replacement-interface-spec.md` and the cutover-side companion to `67-link-and-constellation-join-interface-spec.md`.

## Why this needs its own spec

Resilio's docs are strong enough to make the problem unusually clear.
One article says cloning a Sync instance with plain copies, drive cloners, `dd`, or Time Machine is unsupported.
Another says Windows service install offers `migrate settings and uninstall existing Sync client` versus `clean installation`, where the clean path requires re-sharing and reconnecting existing folders.
Troubleshooting then says switching the service to `Local System` creates a different storage folder, shows no old shares, and requires re-add/re-share from that new context.
Linked-device docs separately warn that linking two already-initialized devices can make one lose its certificate and take over the other instance's folders.
Uninstall guidance says to unlink identity and remove Standard shares first or the old instance will remain visible as offline elsewhere, while hidden `.sync/Archive` bytes still need manual deletion.
Stolen-device guidance escalates to backup, remove shares, unlink identity, remove storage state, reinstall, regenerate identity, relink, and reshare.

The lesson is not that Resilio has no value.
The lesson is that a useful product can still scatter continuity meaning across too many rituals.

AnonSync should therefore make these differences explicit before apply:

- this is same-root re-home vs successor continuity vs blocked takeover
- this candidate keeps its identity vs is bound as reviewed successor
- this runtime/profile opens the same durable state vs a different state universe
- these grants and approvals rewrite vs remain frozen or untouched
- this action revokes predecessor reach now vs leaves known residue for later observation or cleanup

## Core rule

A non-trivial continuity transition should always compile to a reviewed cutover surface.
That includes at least:

- replacing a lost or retired device with a successor
- binding a new machine from imported recovery material
- switching runtime/service profile when the action could open a different state root or authority universe
- re-homing an active state root where continuity, exposure, or mutation posture could change
- any candidate that already has identity or share state and therefore looks more like takeover, migration, or wrong-workflow drift than a fresh join

A channel may compress the review when risk is truly low.
It may not replace the meaning with vague `migrate`, `install as service`, or `replace device` success language.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench `Exits & Replacement` page
- recovery bundle verification or import surface
- state-root / service-profile switch surface
- device detail `Prepare successor` action
- CLI `recover replace-device --plan`
- CLI `state move-root --plan` or `state switch-profile --plan` when continuity is non-trivial

But these must all converge on the same public cutover model.
The operator should never have to wonder whether one surface is doing ordinary state re-home while another is really performing successor continuity, silent identity loss, or fresh-install cleanup.

## Fixed review order

Every non-trivial cutover review should render the same sections in the same order:

1. **Predecessor and candidate**
2. **Continuity carry-forward**
3. **State-root and runtime target**
4. **Share / grant / authority rewrite**
5. **Residue and revocation**
6. **Receipt promise**

### 1) Predecessor and candidate

This section should show:

- predecessor device or runtime context, if any
- candidate device, runtime profile, or target root
- whether the candidate is fresh, imported, already initialized, or drifted
- whether the action is same-root re-home, successor continuity, blocked takeover, or wrong workflow
- whether any prior continuity intent, retirement record, or bundle verification is already attached

The operator must be able to answer: **what exactly is being replaced or re-homed, and is the candidate safe for that job?**

### 2) Continuity carry-forward

This section should show:

- which contacts, grants, share memberships, and policy bindings will carry forward
- which approval memory, direct-path trust, or successor rights will be frozen pending later review
- which state is intentionally dropped rather than preserved
- whether carry-forward depends on verified bundle evidence or live predecessor observation

The operator must be able to answer: **what continuity is actually being claimed here?**

### 3) State-root and runtime target

This section should show:

- target state root path and identifier
- target runtime or service profile
- whether the action opens the same durable root or a different one
- whether control-surface exposure, account/permission posture, or filesystem access changes
- whether restart, quiesce, or attach/import steps are part of apply

The operator must be able to answer: **what durable state and runtime will I be operating after apply?**

### 4) Share / grant / authority rewrite

This section should show:

- which shares, mounts, or claim outcomes will rebind to the candidate
- which grants or approvals rewrite, freeze, or revoke
- whether any re-share, successor, or mutation authority widens
- whether any share remains visible but detached pending later adoption or repair

The operator must be able to answer: **what authority and subject relationships actually change because of this cutover?**

### 5) Residue and revocation

This section should show:

- predecessor residue that will remain after apply
- whether stale route, disclosure, or trust residue waits on offline-peer observation
- whether local bytes, archives, or diagnostics remain intentionally preserved somewhere
- which revocation, cleanup, or follow-up actions remain separate rather than silently bundled

The operator must be able to answer: **what still remains after apply, and what still needs cleanup or observation?**

### 6) Receipt promise

This section should show:

- which receipt will exist after apply
- what it will later prove about predecessor, candidate, carry-forward, runtime target, rewrite scope, and residue
- whether unresolved residue or frozen approvals remain visible through that receipt
- what later audit survives after the draft or recovery bundle is gone

The operator must be able to answer: **what later evidence will prove what this cutover actually changed?**

## Action hierarchy inside cutover review

The primary action should be the safest meaningful next step.
Examples:

- candidate already initialized in a way that looks like takeover → `Review blockers` or `Open replacement comparison`, not `Replace now`
- runtime/profile switch that opens a different root than expected → `Review different root`, not `Continue migration`
- low-risk verified successor with narrow carry-forward → `Prepare cutover` or `Apply cutover` may be primary

Confusing alternatives such as `Migrate settings`, `Take over identity`, or `Adopt old shares` should be visually separate and usually plan-bearing.

## What the surface must never imply

The cutover surface must never imply that these are the same thing:

- replacing a dead machine vs opening the same root under a different runtime profile
- preserving continuity vs creating a fresh empty context
- rebinding grants vs merely restoring visibility
- revoking predecessor authority vs only hiding its stale row
- verified successor binding vs unsupported clone-like takeover

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## Linux/WebUI parity rule

A Linux-first product has to assume that WebUI, TUI, CLI, and headless automation are not edge cases.
So the reviewed cutover grammar must survive across those channels.
It is not acceptable for one richer surface to show predecessor/candidate, carry-forward, and residue truth while Linux/WebUI falls back to a generic install or migrate success path.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync plan show <id> --view review` for recovery/state-transition plans.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether they are replacing one device safely, reopening the same durable state, or accidentally creating a different state universe.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed cutover grammar is how the archive avoids rebuilding a system where replacing hardware or moving runtime context is individually scriptable and individually convenient, yet the full meaning still depends on which installer, service, or link prompt happened to appear first.
