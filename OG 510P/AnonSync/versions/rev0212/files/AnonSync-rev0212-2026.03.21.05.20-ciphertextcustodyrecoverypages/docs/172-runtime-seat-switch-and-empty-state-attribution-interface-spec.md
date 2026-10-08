# Runtime-seat switch and empty-state attribution interface spec

## Purpose

The archive already has execution-seat doctrine, state-root objects, local-web-first bringup, and shell/context rules.
What it still lacked was one concrete interface contract for **the moment a different runtime seat opens and the product appears empty**:

> when the operator launches through a different service account, runtime seat, or control surface and sees no subjects, what page tells them whether this is a clean empty root, a different attached root, a permission-limited seat, or an honest failure to attach the prior state universe?

Current Resilio docs keep this seam concrete.
Changing service account can expose a different storage folder, the UI can then show a welcome/empty state with no old shares, configuration files load from the seat-specific storage folder, and WebUI reachability can differ between localhost-only and broader listen posture.
AnonSync should not let `empty` stand in for all of that.

## Core decision

Any surprising empty state reached through seat/profile change must open an **empty-state attribution** surface.
The system must classify the emptiness before suggesting create/import/attach actions.

## Empty-state classes

The attribution surface must distinguish at least:

1. **True empty root** — active root is attached and genuinely contains no subjects
2. **Different root attached** — this seat opened another valid root than the one the operator expected
3. **Prior root known but unattached** — the product can identify the older root and offer reviewed attach/switch
4. **Root inaccessible from this seat** — the expected root exists but the seat lacks reachability or permission
5. **Policy-restricted control seat** — seat is attached read-only / inspect-only and therefore suppresses ordinary actions

## The fixed review order

Every seat-switch empty-state case should render sections in this order:

1. **Current seat and observed state**
2. **Active root answer now**
3. **Other known roots or expected roots**
4. **Reachability and control-surface differences**
5. **Safe next actions**
6. **Receipt promise**

## 1) Current seat and observed state

Show:

- current execution seat / service profile
- how the operator arrived here (local web, service, workstation, recovery CLI, other)
- whether the page was opened after seat switch, restart, first run, or attach failure
- the observed condition (`empty shell`, `welcome`, `inspect-only`, `attach blocked`, other)

The operator should be able to answer:

> what local world am I actually in right now, and why does it look empty?

## 2) Active root answer now

This section must say plainly:

- which state root is active
- where it lives
- whether it is new, known, imported, or seat-local default
- whether its emptiness is genuine or provisional because attach failed

Good top-line states include:

- `active root is empty`
- `different root attached from prior session`
- `expected root not attached`
- `expected root unreachable from this seat`

## 3) Other known roots or expected roots

If the product has evidence of a prior or alternate root, show:

- root IDs and human labels
- last seen seat
- last seen time
- whether the current seat may attach them
- whether attachment would preserve identity continuity or requires review

This prevents `no subjects` from hiding a much more specific truth: the operator is in the wrong local world.

## 4) Reachability and control-surface differences

The attribution page should then explain:

- localhost-only vs remotely reachable control surface
- different service account or namespace visibility
- missing write permission to prior targets
- config file / root discovery location differences by seat
- whether the current control surface is semantically full, degraded, or inspect-only

This helps the operator distinguish `I opened a different seat` from `the product lost my data`.

## 5) Safe next actions

Good primary actions include:

- `Attach expected root`
- `Switch back to prior seat`
- `Inspect inaccessible root requirements`
- `Continue with true empty root`
- `Open seat-switch review`

Bad primary actions include:

- `Create first share`
- `Get started`
- `Import now`

when the system already knows the emptiness is probably caused by seat drift.

## 6) Receipt promise

The resulting receipt or audit record must prove:

- which seat was active
- which root was attached or expected
- how the emptiness was classified
- what next action the operator chose
- whether identity continuity or subject inventory changed afterward

A later reader should be able to answer:

> was the product actually empty, or did we simply open a different runtime seat and then choose what to do about it?

## What must never happen automatically

The product must never automatically:

- treat a seat-caused empty state as though it were first run
- encourage creation/import before classifying known roots
- hide the active state root because the control surface looks simpler empty
- imply data loss when the sharper truth is path/seat/root drift

## Why this is worth the trouble

`No shares visible` is one of the easiest local failures to misread.
A good product should turn that from panic into classification: which seat, which root, which world, and what honest next step follows.
