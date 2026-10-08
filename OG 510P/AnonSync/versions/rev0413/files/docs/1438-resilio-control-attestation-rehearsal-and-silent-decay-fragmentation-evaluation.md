# Resilio control-attestation, rehearsal, and silent-decay fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- close a case honestly
- promote a guardrail from that case
- activate the guardrail with scope, owner, anti-claims, and recurrence watch

What it still lacked was one ordinary operator answer to the next harder question:

> why do we still trust this guardrail later, especially when the hazard has not repeated and the environment has quietly changed underneath it?

That is the seam this pass locks.
A real operator cannot wait for the next damaging repeat just to learn whether a control still works.
The product needs a first-class answer for **attestation, rehearsal, and silent trust decay**.

Current official Resilio material is useful here because it already shows that control truth can silently drift across surfaces and worlds:

- `Power user preferences`
- `Folder Preferences`
- `Running Sync in configuration mode`
- `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?`
- `Running Sync as a service on Windows`
- `Sync Service Troubleshooting on Windows`
- `Settings on mobile platforms`
- `Running Sync on schedule`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Power user preferences` still says the article covers the latest version and older versions may miss settings or still have deprecated ones. It also still includes options that are restart-bound (`profiler_enabled`) and one that is explicitly ignored in Linux WebUI. That means some controls are version-sensitive, apply-sensitive, and surface-sensitive by construction.
- `Folder Preferences` still says folder-level controls are available on desktop platforms only. So a visible guardrail on one surface does not automatically imply parity across mobile or service-admin worlds.
- `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?` still requires disabling tracker and relay both in share preferences and in power-user settings, then restarting Sync, and even warns that previously cached global IP state can keep internet syncing alive until peer-expiration/cache-reset steps are performed. That is a textbook example of why a control needs attestation instead of mere configuration intent.
- `Running Sync in configuration mode` still says the same settings can be applied on multiple machines and Advanced Preferences parameters can be added, but also says a non-default `storage_path` creates new settings there, config mode can set up only Standard folders, and config-authored shared folders disable WebUI and override folders previously added from WebUI. So a control can appear standardized while actually moving into a different authorship world.
- `Running Sync as a service on Windows` still distinguishes migrated settings from clean installation, with the latter requiring re-share and reconnect. So the same nominal service adoption can either preserve or reset control posture.
- `Sync Service Troubleshooting on Windows` still says switching to `Local System` requires restart and then yields a new storage folder with no old added folders, requiring re-add / re-share or reconnect. That is a silent trust-break if the product only remembers the intended control but not the post-switch proof.
- `Settings on mobile platforms` still shows mobile-specific settings such as battery saver, auto-start, mobile-data gating, and Android `Simple mode`, proving that some settings/control assumptions are lane-specific rather than globally attestable.
- `Running Sync on schedule` still exposes a weekly scheduler in Sync Preferences -> Advanced and notes version/licensing limits. That is a real control ingredient, but not by itself an attested claim that the intended schedule is still the effective governing control everywhere.

So current Resilio still clearly admits serious attestation truths:

- some controls span multiple surfaces
- some controls require restart before they are real
- some controls are version-bound or deprecated over time
- some controls are world-bound because config/service choices can fork state
- some controls are lane-bound because desktop and mobile settings diverge
- some controls can retain stale cached behavior after the nominal setting change

But those truths still do not become one operator-facing **control trust / attestation / rehearsal / trust-withdrawal** object.

## What Resilio still gets right

### 1) It is candid that control truth is not always one toggle

The LAN-only article is especially useful because it openly spans share preferences, power-user settings, restart, and cached peer-state cleanup.
That is exactly the kind of multi-surface truth worth borrowing.

### 2) It exposes world-fork and version-fork hazards

Config mode, service migration, Local System switching, and latest-version-only power-user docs all show that a control can decay or move worlds without changing its friendly label.
That honesty is useful.

### 3) It preserves some activation and scope details

Desktop-only folder preferences, mobile-only settings, and restart-bound settings are all real scope boundaries.
Those should stay explicit.

## Where current Resilio still fragments the operator answer

### A) Intended configuration is still too easy to confuse with trusted control

A careful operator can set the right checkboxes and config values.
But the product still does not answer in one place:

- whether the control was actually activated everywhere
- whether all prerequisites still hold
- whether a world fork invalidated the old claim
- whether the proof is fresh or stale
- what kind of witness would re-earn trust without waiting for an incident

### B) Real incidents remain over-weighted as the only serious proof

Resilio gives live operation pages, settings pages, troubleshooting pages, and service/config notes.
What it does not give is one explicit answer to:

- can this control be attested by a live read-only check?
- does it need a synthetic drill?
- is passive silence meaningful enough?
- when must trust be withdrawn even without a visible incident?

### C) Silent decay is not first-class

Version change, ignored settings, service storage shift, config authorship shift, desktop/mobile mismatch, or stale cached peer state can all weaken a control.
But there is still no one page that says `this control is active but stale`, `this control is now untrusted`, or `this control needs rehearsal before any stronger claim is safe again`.

## Hard product decision unlocked by this pass

AnonSync should not let `configured`, `active`, and `trusted` collapse into one status.
It should promote every meaningful guardrail into a first-class object that can separately be:

- `configured`
- `applied`
- `attested-live`
- `attested-by-rehearsal`
- `passively-trusted-within-window`
- `stale`
- `trust-withdrawn`

That is the right next seam because it answers the operator question that always follows control promotion:

> do we still trust this control right now, and why?

## Replacement line for AnonSync

Borrow from Resilio:

- candor that some controls span multiple surfaces and require restart
- honesty that service/config choices can fork worlds
- explicit scope boundaries across desktop, service, and mobile lanes

Do not clone from Resilio:

- any contract where a stored setting can masquerade as a trusted control
- any workflow that waits for the next incident to rediscover silent control decay
- any product shape where the operator must reconstruct control trust from settings pages, service KBs, and version memory

AnonSync should instead ship explicit pages for:

- control attestation contract
- attestation review
- rehearsal proof
- control decay timeline
- attestation lineage receipt
