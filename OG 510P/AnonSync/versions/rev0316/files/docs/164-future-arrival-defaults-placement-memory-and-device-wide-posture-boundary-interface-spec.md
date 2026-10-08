# Future-arrival defaults, placement memory, and device-wide posture boundary interface spec

## Purpose

The archive already separates visibility, claim, bind, and materialization.
What it still lacked was a precise answer to the standing-default seam:

> how much may a machine-level future-arrival posture decide for later incoming shares before the product starts hiding one-share placement intent inside device-wide convenience?

Current Resilio docs make the danger clear.
Linked devices can use device-level synchronization modes for future arrivals, and operators are told to switch a whole device into `Disconnected` when they want safe manual placement for one incoming share.
AnonSync should not clone that boundary.

## Core decision

Standing defaults may shape **suggestion** and **initial lane placement**.
They must not silently determine one-share bind outcomes when local path choice, compare review, or authority review is still non-trivial.

That means the product must keep four things visibly separate:

1. arrival visibility default
2. default materialization posture
3. placement suggestion memory
4. actual per-share claim / bind decision

## What standing defaults are allowed to do

A standing default may decide:

- whether newly visible incoming subjects land in `Now`, `Soon`, `Quiet`, or an inbox family
- the suggested materialization posture for low-risk future claims
- the suggested root or path template to propose later
- whether routine same-person arrivals may start as `visible here` without immediate attention

Those are convenience aids.
They are not yet local acceptance.

## What standing defaults are not allowed to do

A standing default may not, by itself:

- create a path inside a non-empty target
- override compare blockers
- widen role or approval memory beyond reviewed policy
- convert identity-sensitive relationship work into ordinary arrival work
- force the operator to change the whole device posture merely to place one share safely

That last point is crucial.
Device posture is not the escape hatch for one-share path safety.

## Default families

The product should expose at least these standing defaults explicitly:

### 1) Visibility default

Examples:

- announce immediately
- announce quietly
- suppress until review lane opens

### 2) Materialization suggestion default

Examples:

- visibility only
- metadata / placeholder first
- selective local materialization suggested
- full local materialization suggested

### 3) Placement suggestion default

Examples:

- suggest root `~/AnonSync/Incoming`
- suggest per-subject remembered root
- suggest workspace-scoped path template
- no suggestion

### 4) Approval / auto-claim boundary

Examples:

- never auto-claim
- same-seat low-risk auto-draft only
- same-person trusted arrivals may skip inbox but still require bind review

The product should not compress these into one overloaded `Sync mode` selector.

## The future-arrival card

A machine or seat should have one `Future arrivals` card that states:

- what later arrivals will become visible as
- what local materialization is only suggested versus actually automatic
- what path memory will be proposed later
- which classes still force per-share review regardless of standing defaults

The operator should never have to guess whether a machine-level default affects only presentation, only suggestion, or actual bind behavior.

## Per-share boundary at claim time

When a real incoming share appears, the claim page must restate:

- which standing default influenced this arrival
- which parts are still only suggestions
- which stronger review was triggered by this share's actual risk
- whether remembered path or role memory was applied, ignored, or blocked

This is how the product keeps machine posture from becoming hidden local fate.

## Remembered placement rules

Remembered successful binds may inform later suggestions.
They should be treated as graded memory, not destiny.

The product should distinguish:

- same subject, same seat, strong remembered path
- same family, same seat, weak suggestion only
- same seat but conflicting bytes now present
- remembered path exists but stronger policy now disagrees

Memory may pre-fill a suggestion.
It must not erase compare review when the current target is non-empty, conflicting, or otherwise risky.

## Good primary actions

Examples:

- `Prepare claim`
- `Review suggested path`
- `Use remembered path after compare`
- `Keep visible only for now`
- `Adjust future-arrival defaults`

Bad primary actions include:

- `Turn device to disconnected so you can place this one safely`
- `Switch mode and try again`

Those labels reveal that the product has let one-share semantics leak into whole-device posture.

## Cross-projection rules

GUI, local web, TUI, and CLI may expose future-arrival defaults differently.
They must preserve:

- the distinction between visibility default and local bind
- the distinction between suggestion and actual apply
- the reason a particular share escalated beyond standing defaults
- the ability to override one share without mutating the whole machine posture

## Result

A good standing-default contract prevents five failures:

- device-wide mode standing in for per-share placement review
- path suggestion turning into silent path creation
- remembered convenience erasing current compare blockers
- future-arrival defaults being too vague to audit later
- one awkward share forcing the operator to rewrite whole-machine posture just to stay safe

If the easiest safe path for one incoming share still requires changing machine-wide arrival mode first, AnonSync has not yet drawn the right boundary.
