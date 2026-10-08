# Resilio invocation profile, launch switch, and runtime-world fragmentation evaluation

## Why this pass exists

The archive already had strong pages for runtime seats, state roots, same-host namespaces, control surfaces, and mutation durability.
What it still did not own with one explicit current Resilio memo was a narrower but very ordinary operator seam:

> when I launch this thing with these flags, from this account, in this mode, what world am I actually starting, where will state live, what control exposure follows, and is this a quiet reopen or a different runtime entirely?

Current official Resilio docs still make that seam materially real.
They still say Windows launch switches such as `/config`, `/webui`, `/storage`, `/noinstall`, `/S`, and `/minimized` are available.
They still say Linux/headless launch flags such as `--config`, `--storage`, `--identity`, `--license`, `--nodaemon`, and `--webui.listen` materially change where state lives and who can reach control.
They still say a non-default `storage_path` in config mode creates settings there, that service config mode only works from the service storage, that a service-account switch can expose a new empty-looking world with a different storage folder, and that updating a non-default `/config` or `/storage` launch requires using the same command parameters and the same user to preserve configuration.

That is strong candor.
It is also a good reason not to clone the contract directly.

## What current Resilio still gets right

Current official docs still publish several truths worth borrowing:

- **Launch switches are admitted as semantic, not cosmetic.** The Windows CLI doc still says `/config` starts config mode, `/storage` changes the storage folder, `/webui` forces browser-open on loopback only, `/noinstall` avoids installation and uses the default app-data storage, `/S` hides the program interface, and `/minimized` suppresses the main window while leaving tray access.
- **Linux launch posture is candidly stateful.** The Linux guide still says `--storage` selects where settings, identity, and license live; without it, a `.sync` folder is created in the current directory; `--identity` and `--license` will also use that default storage unless a storage path is supplied; and `--nodaemon` changes whether the process backgrounds itself.
- **Control exposure is admitted as launch-shaped.** The Linux guide still says WebUI listens on `127.0.0.1` by default, can be widened to `0.0.0.0` or a specific interface, and can even fail hard if pinned to a specific interface that later is unavailable.
- **Config mode is admitted as a world selector.** The config-mode guide still says a non-default `storage_path` creates settings there, and service config mode works only when the config file is placed in the service storage.
- **Service-user shifts are admitted as storage-world shifts.** The Windows service troubleshooting guide still says switching to Local System yields a new storage folder, an empty-looking roster, and a re-add / re-share burden.
- **Update continuity is admitted as launch-discipline dependent.** The current v3 update guide still says non-default `/config` or `/storage` launches must be restarted with the same command parameters, and Linux binary installs must be relaunched with the same command-line parameters and the same user to preserve configuration.

That is all good product honesty.
Resilio does not pretend that `start the app` is one flat verb.

## Where current Resilio still stays too article-shaped

### 1) Invocation intent is still reconstructed from flags

The ordinary operator should not have to reconstruct from CLI help, Linux notes, config-mode notes, and service docs whether a launch means:

- same world, visible desktop window
- same world, quiet background session
- same world, loopback-only control endpoint
- same world, LAN-exposed control endpoint
- sibling world through a different storage root
- clean world through an implicit current-directory `.sync`
- service world through a different account
- config-owned world whose values outrank interactive edits

Yet that is still roughly how present-day Resilio explains the territory.

### 2) Hiddenness and sameness still blur together

`/S`, `/minimized`, service launch, headless Linux, and `/webui` browser-open all change what the operator can see.
But some of those are the same durable world made quieter, while others can surface a genuinely different storage or control world.
Current docs preserve that truth, but not as one stable invocation contract.

### 3) State-root choice still looks easier than it is

Current docs are candid that `/storage`, `--storage`, config `storage_path`, current-directory `.sync`, and service-user storage roots materially affect settings, identity, license, and databases.
That means launch itself can be a state-adoption act.
AnonSync should not clone any contract where storage-root selection still reads like a mere expert convenience.

### 4) Exposure and quietness still piggyback on flags instead of reviewed plans

`/webui` implies loopback-only reach.
`--webui.listen 0.0.0.0:8888` exposes LAN reach.
A pinned but unavailable interface can abort startup.
`/S` and `/minimized` change what the operator sees without changing the underlying need for stop truth, drain truth, and proof surfaces.
These are review-worthy launch effects, not only power-user lore.

### 5) Preservation through update still depends on remembered invocation ritual

Current official update docs still say continuity for non-default launches depends on relaunching with the same parameters and same user.
That is operationally correct.
It is also a strong sign that invocation profile is part of durable product truth and should not remain hidden in admin notes.

## What AnonSync should do instead

AnonSync should treat **invocation profile** as a first-class reviewed object.
Launching should still be fast when the decision is low-risk and same-world.
But the product should never pretend that state root, exposure, quietness, and world lineage are merely incidental.

The replacement contract should own five surfaces:

1. **Invocation profile contract sheet**
   - launch intent
   - invocation family
   - state-root authority
   - visibility grade
   - control exposure grade

2. **Launch review**
   - same-world reopen vs sibling-world fork vs clean-world start vs blocked overlap
   - state adoption / continuity effect
   - exposure and visibility deltas
   - required follow-up proofs

3. **Quiet-runtime proof**
   - hidden window vs tray vs service vs headless
   - what still runs
   - how control is reached
   - what stronger `stopped` or `not exposed` sentence is blocked

4. **Launch world preview**
   - chosen storage root
   - config-owned values
   - current-directory or implicit default roots
   - service-account or user-dependent world switch risk

5. **Invocation receipt**
   - reviewed intent
   - actual world opened
   - visibility and exposure posture
   - state-root lineage verdict
   - blocked stronger sentence

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that launch switches, storage roots, loopback-vs-LAN WebUI, service accounts, and same-parameter relaunch discipline materially change the runtime world. But it is not worth cloning the way operators still have to reconstruct, from CLI help, Linux notes, config-mode instructions, service troubleshooting, and update guides, whether a given launch is a quiet same-world reopen, a sibling runtime, a fresh storage world, or a newly exposed control endpoint.
