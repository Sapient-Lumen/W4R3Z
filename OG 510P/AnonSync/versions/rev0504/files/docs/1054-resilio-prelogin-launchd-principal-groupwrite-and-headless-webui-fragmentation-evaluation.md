# Resilio pre-login launchd, principal shift, group-write, and headless-WebUI fragmentation evaluation

## Why this pass exists

The archive already had invocation profile, service-world continuity, control exposure, and storage-world lineage.
What it still did not own cleanly enough was one narrower but very ordinary operator seam:

> when a Mac operator wants Sync to run before any user logs in, did they merely enable an earlier startup point, or did they create a new execution world with a different principal, a new POSIX write contract, a headless control surface, and extra mode caveats?

Current official Resilio docs still make that seam materially real.
They still say all of the following at once:

- the ordinary Mac app starts when the user logs in and runs under the current user account
- to run with no logged-in user, the operator must use `launchd`, create a **new user**, and grant **root-level** launch permission
- the sample headless config explicitly flips `use_gui` to `false`, moves storage to the new user's home, and opens WebUI on `0.0.0.0:8888`
- the launchd recipe sets `RunAtLoad`, `KeepAlive`, `UserName`, and `Umask 2`, and uses a helper script with a built-in 90-second delay before the process actually starts
- the same article warns that the chosen POSIX/umask model means delivered files become group-writable and that newly created files inside synced folders must also preserve group write or Sync will stop syncing them
- the same article adds an extra selective-sync caveat: if placeholders are wanted, the operator is told to set `"enable_placeholders": false` in `myconfig.json`
- current WebUI docs separately say WebUI on app installs is configuration-file driven, that `0.0.0.0` widens audience to the LAN, that HTTP is default unless `force_https` is set, and that adding shares by clicking a link in WebUI does **not** work and must be done manually through `+ -> Enter a key or link`
- current background-behavior docs separately say ordinary desktop background use on macOS can simply mean minimizing the UI, which is a materially different story from pre-login launchd service-emulation

That is useful candor.
It is also a strong reason not to clone the present contract.
One ordinary operator answer — `what exactly changed when I made Sync run before login?` — still depends on combining:

- the Mac pre-login recipe
- generic WebUI configuration docs
- generic background-behavior docs
- config-mode knowledge
- local POSIX permission intuition

AnonSync should keep the distinctions and refuse the archaeology.

## Hard product decisions locked by this pass

1. **Pre-login startup is a mode change, not a convenience toggle.** It creates a distinct execution-world class with its own principal, storage home, and control exposure.
2. **File-creation discipline is part of runtime truth.** If the chosen principal/umask requires future local writers to preserve group write, that is a first-class contract, not a support-note footnote.
3. **Headless control audience is reviewed separately.** `use_gui: false` plus `listen: 0.0.0.0` is not just a launch recipe; it is a control-surface widening.
4. **Session affordance losses are explicit.** A pre-login headless runtime can lose ordinary handler and tray-shaped behavior even while bytes still sync.
5. **Receipts preserve launch witness and caveats.** Launch class, start delay, principal, storage world, control audience, and POSIX write contract belong in one durable record.

## What current Resilio still gets right

Current official docs still publish several truths worth borrowing.

- **It admits that pre-login on Mac is exceptional.** The current article does not pretend there is one harmless checkbox; it says launchd, root permissions, and a dedicated user are required.
- **It admits that principal and filesystem semantics matter.** The same article explicitly warns that POSIX permissions and umask can break sync if the operator does not maintain the expected group-write posture.
- **It admits that headless control is configuration-shaped.** Current WebUI docs still say app-install WebUI is driven by config and that listening on `0.0.0.0` widens reach.
- **It admits that transport security is a separate choice.** Current WebUI docs still say HTTP is default and that HTTPS requires extra config, with self-signed warning behavior unless the operator supplies their own certificate.
- **It admits that handler parity is incomplete.** Current WebUI docs still say link-click adding is not supported in WebUI and must be re-entered manually.
- **It preserves the difference between hidden and pre-login runtime.** Current background docs still say ordinary macOS background use can simply be the minimized app, which keeps pre-login launch from being mislabeled as the same thing.

That is good product honesty.
Resilio does not flatten all startup shapes into one story.

## Where current Resilio still stays too article-shaped

### 1. Pre-login launch still hides behind a recipe instead of a product contract

The current article is candid, but it is still a recipe.
The operator still has to infer the product meaning:

- new user means new execution principal
- new home path means new storage world
- `use_gui: false` means headless control mode
- `0.0.0.0` means widened control audience
- `Umask 2` means future file-creation obligations

AnonSync should not leave that inference burden in shell/plist prose.

### 2. Principal shift and file-creation contract are not reviewed together

The warning that new files must preserve group write or Sync will stop syncing them is unusually important.
Yet it is tucked inside setup instructions.
The operator should get one clear answer to:

- which principal owns the runtime
- which users can read/write delivered bytes
- what ownership/mode class future local files must satisfy
- what the exact failure mode is if that contract is violated

### 3. Headless control exposure still mixes with setup convenience

Current docs do say to listen on `0.0.0.0:8888` and provide login/password in the sample.
Current WebUI docs separately say HTTP is default unless HTTPS is forced.
But the product still lacks one owned review of:

- loopback-only versus LAN-exposed control
- HTTP versus HTTPS posture
- password presence versus absence
- who can now reach the control surface because of pre-login mode

### 4. Session-affordance losses remain scattered

The operator still has to remember from separate docs that:

- WebUI link-click intake does not work
- headless mode uses WebUI rather than ordinary app UI
- ordinary minimized background mode is a different thing than pre-login launchd
- placeholders/selective-sync in the Mac recipe require a caveat-setting change

That is too much for one ordinary `run before login` decision.

### 5. Start timing and keepalive semantics remain operational folklore

The sample helper script includes a 90-second sleep and the plist sets `KeepAlive`.
Those are not harmless implementation details.
They change what `should already be running`, `just rebooted`, and `launch successful` ought to mean.
AnonSync should not clone a world where start witness remains shell-script memory.

## The tighter non-clone decision

Borrow Resilio's candor that pre-login launch on macOS is materially different from ordinary background use; that execution principal, storage home, group-write discipline, and control audience are real consequences; and that headless mode loses some ordinary affordances.
Do **not** clone a product contract where the operator still has to merge a launchd recipe, WebUI notes, background-behavior prose, and POSIX intuition to answer what world now exists and what local-write contract it imposes.

## What AnonSync should do instead

AnonSync should treat **pre-login runtime on workstation-class hosts** as one first-class reviewed family.
Every serious `run before login`, `run headlessly`, `switch execution user`, or `widen headless control audience` mutation should answer five things in one place:

1. **launch class** — session-bound app, sessionless launchd/service runtime, or policy-managed daemon
2. **principal and storage world** — which account owns the runtime and where its world lives
3. **file-creation contract** — what ownership/mode class future local writes must satisfy
4. **control-surface audience** — loopback-only, LAN-exposed, or stronger-transport-bound headless control
5. **mode caveats** — lost handler paths, placeholder limits, start delay, and other non-parity costs

## New page obligations from this pass

The archive now needs five more workflow-owned pages:

- **Pre-login runtime contract sheet**
- **Headless launch review**
- **Group-write discipline proof**
- **Pre-login mode caveat page**
- **Pre-login lineage receipt**

Those pages should sit beside invocation profile, service promotion, control-surface grade, and storage-world lineage pages — not underneath setup instructions alone.
