# Resilio stop proof, hidden runtime, and shutdown fragmentation evaluation

## Why this pass exists

The archive already had strong work on route exposure, activation timing, contested repair, and substrate topology.
What it still lacked was one narrower current Resilio pass about another ordinary operator question:

> did I actually stop sync, or did one projection merely disappear while the runtime can still publish, index, transfer, or restart later?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `Running Sync as a service on Windows` still says Sync can run automatically in the background regardless of whether a user is logged in, and can run as `System`, `Local Service`, or current user.
- `Sync interface on Android` still gives `Exit` its own explicit command and says it `shuts Sync down correctly`.
- `Does Sync work in background?` still says Android may continue in the background unless killed by task killers or memory optimizers, while iOS background synchronization is unavailable.
- that same background article still warns that shutting down and re-opening re-indexes folders and can change overwrite chronology after offline edits.
- `Settings on mobile platforms` still says disabling Android notifications lowers Sync priority and may force it to stop working in the background.
- `Sync Preferences` still exposes `Start Sync on startup`, which means stop truth includes automatic future revival.
- `Updating Sync to latest version` and related install/update docs still distinguish stopping the app, service, or process according to install mode.

That is a good reason to keep studying Resilio.
It is also another good reason not to clone the exact interface contract.

## What current Resilio still gets right

### 1) It admits that not all forms of “gone from view” mean “stopped”

Current docs do not flatten `service running`, `background mobile runtime`, `closed UI`, and `explicit Exit` into one answer.
That honesty is valuable.

### 2) It admits that platform/runtime class changes stop meaning materially

Current docs still preserve that Android background behavior, iOS foreground-only transfer, and Windows service/background execution are different runtime contracts.
That distinction is worth keeping.

### 3) It admits that stop/start boundaries can be chronology-shaping

Current background docs still warn that shutdown and re-open can re-index and alter overwrite chronology after offline edits.
That means stop is not just cosmetic lifecycle trivia.

## Why AnonSync still should not clone it

### 1) One ordinary answer still spans too many pages

To answer `did it really stop?` the operator may still need to combine:

- Windows service/background docs
- Android interface docs
- mobile background caveats
- notification-priority notes
- startup settings
- install/update stop instructions
- re-open chronology warnings

That is too much archaeology for one ordinary stop decision.

### 2) Projection state and runtime state are still too easy to confuse

Current Resilio preserves the facts, but the operator can still be pushed to infer whether the vanished thing was:

- only a foreground projection
- only a tray / browser shell
- the current process
- the background runtime
- the long-lived service
- or all publication lanes together

AnonSync should not leave that distinction scattered.

### 3) Drain completion is still not owned as one reviewed artifact

Current docs distinguish stop methods and background/runtime survival, but do not turn `pending work`, `draining`, and `proven no-further-publication` into one obvious product-owned review.
AnonSync should.

### 4) Restart posture is still more settings-and-platform lore than one contract sheet

`Start on startup`, mobile background priority, service install mode, and reopen chronology are all parts of one operator reality: stop truth is incomplete unless revival and restart cause are visible.
AnonSync should productize that as one page family.

## Hard decisions now locked for AnonSync

1. **Stop is a first-class contract object.** `close`, `hide`, `pause`, `background`, `service still running`, `draining`, and `full stop` are separate states.
2. **Projection disappearance never equals runtime stop.** The product must say when bytes may still move.
3. **Drain completion and no-further-publication proof are separate from stop intent.** A stop request is not a proven quiet boundary.
4. **Automatic restart posture is public.** Startup-on-boot, service install, mobile background privilege, and watchdog relaunch are part of the contract.
5. **Restart provenance remains durable.** Re-open cause and chronology risk stay visible.
6. **Every consequential stop mutation emits a receipt.**

## Replacement page family justified by this pass

This pass therefore justifies six more product-owned surfaces:

- **Runtime stop contract sheet**
- **Shutdown drain review**
- **Runtime stop proof**
- **Restart provenance page**
- **Runtime stop receipt**
- **Stop drift / silent relaunch alert**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right to admit that background execution, services, explicit exit, startup revival, and restart chronology change the real stop contract. But it still makes one ordinary operator answer — `did I actually stop sync, or did one surface just disappear while work may continue or restart?` — depend on service docs, mobile background notes, startup preferences, and update instructions instead of one stable page family. AnonSync should keep the candor and refuse the archaeology.
