# Shell-surface activation proof page, Finder/Explorer extension state, filesystem eligibility, and registration truth interface spec

## Purpose

The host-integration contract says what shell surfaces were requested.
This page proves whether they are actually live.

The practical question is:

> are shell affordances absent because the product is broken, because the host never activated them, because the target filesystem is ineligible, or because another app or policy owns that extension space?

Current official Resilio docs still make this seam concrete:

- share-related context menus depend on Selective Sync being on
- Windows context items appear only on NTFS volumes
- shell-extension DLLs must exist and be registered
- Explorer/Finder may need restart/relaunch before the host surface catches up
- macOS Finder extensions may need explicit enablement in system settings or `pluginkit`
- other apps can conflict for the same extension space
- Windows may require `EnableLUA=1` for the shell surface to function

AnonSync should therefore model shell activation as a proof workflow rather than a troubleshooting afterthought.

## When this page appears

Render this page when any of the following is true:

- a shell surface was requested during install or later host integration
- the operator reports missing Finder/Explorer/context-menu affordances
- the target path sits on a filesystem with known eligibility limits
- the host shows registration or extension conflicts
- the product is about to claim that shell integration is active

## Proof ladder

### 1) Requested surface

Show:

- requested surface kinds
- feature prerequisites
- target path / target subject class
- whether the surface is even meaningful for the chosen mode

Proof classes:

- `requested`
- `not-requested`
- `inapplicable`

### 2) Eligibility proof

Show:

- filesystem eligibility
- feature-flag eligibility
- OS policy eligibility
- whether the host path is inside the scope where shell affordances should appear

Proof classes:

- `eligible`
- `ineligible-filesystem`
- `ineligible-feature-state`
- `policy-blocked`
- `unknown`

### 3) Registration proof

Show:

- extension binary/apex presence
- registration state
- version match
- host-recognized identifier

Proof classes:

- `registered`
- `present-unregistered`
- `missing-binary`
- `stale-registration`
- `unknown`

### 4) Host-uptake proof

Show:

- Explorer/Finder restart requirement
- extension enabled/disabled state
- conflict signals from other apps
- reboot necessity if hooks are still pinned

Proof classes:

- `active`
- `restart-pending`
- `conflicted`
- `reboot-pending`
- `inactive`

### 5) Claim ceiling

Show:

- strongest safe sentence
- blocked stronger sentence
- next witness needed for stronger claim

Examples:

- strongest safe: `shell extension is registered, but host uptake is still pending Explorer restart`
- blocked stronger: `context menu is active everywhere this runtime touches`

## Main surface

A compact result should read like one of these:

- `eligible NTFS target · extension registered · Explorer uptake still pending`
- `surface requested, but target path is ineligible for shell affordance proof`
- `Finder extension enabled but conflicted with another app; live menu claim withheld`
- `registration missing; host integration exists, shell activation does not`

## Required copy blocks

### Strong proof

`Shell-surface activation is proven only where eligibility, registration, and host uptake all align.`

### Weak proof

`The product asked for shell integration, but the host has not yet proven that the requested surface is live.`

## Event language

Use phrases such as:

- `shell activation proof refreshed`
- `filesystem eligibility failed`
- `registration repaired`
- `host uptake still pending`

Avoid phrases such as:

- `context menu fixed`
- `Finder works now`
- `integration complete`

## Design tests

The page fails if any of these remain true:

- Selective Sync or filesystem prerequisites are buried outside the proof flow
- registration and host uptake collapse into one binary state
- extension conflict looks like random breakage instead of a distinct proof class
- the interface can claim `integrated` without naming where the shell surface is actually proven
