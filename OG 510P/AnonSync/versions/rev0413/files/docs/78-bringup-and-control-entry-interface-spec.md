# Bring-up, continuity selection, and control-entry interface spec

The archive already has state-root, control-access, recovery, and cutover specs.
This document answers the earlier operator question those layers still leave open:

> what must a real bring-up surface literally show before a host starts fresh, reopens known state, imports recovery, performs continuity-sensitive replacement, or exposes first control access, so the product does not drift back into installer, config-file, or activation ritual?

This is the front-door companion to `42-state-root-and-service-profile-spec.md`, the access-entry companion to `55-control-access-and-session-boundary-spec.md`, the continuity-sensitive first-open companion to `68-successor-cutover-and-rehome-interface-spec.md`, and the first-control companion to `56-recovery-material-and-continuity-bundle-spec.md` when the problem is not “how do I recover later?” but “what exactly am I opening right now, under which identity, with which control posture, and how should that first entry be reviewed?”

## Why this needs its own spec

Resilio's current docs make the seam unusually visible.
`Important before updating to Resilio Sync 3.0.0`, `Licensing in Resilio Sync 3.0`, and the v3 changelog show that edition family, activation model, and supported architecture materially affect what kind of install or update is even honest.
`Running Sync in configuration mode` and `Guide to Linux, and Sync peculiarities` then show that headless/server bring-up depends on startup flags and config-file fields such as `--storage`, `--identity`, `--license`, and `--webui.listen`, with localhost default, LAN exposure achieved by `0.0.0.0` or specific interfaces, and even shutdown risk if the chosen interface is not actually present.
`How to apply license key and share license seats` adds more first-entry ritual: on headless systems identity creation and license application are separate steps.
`Cloning Sync` separately says plain copying an instance is unsupported.

Those documents are individually useful.
Together, they still scatter one important operator truth:

- is this host starting fresh, reopening known durable state, importing recovery material, or accidentally opening the wrong control universe
- is identity continuity fresh, retained, successor-sensitive, or only inspectable pending review
- what control endpoint is about to exist, where it listens, and who can reach it
- whether the system is truly ready for first control entry or still blocked by platform, root, permission, recovery, or exposure prerequisites
- whether a friendly-looking startup is actually a continuity-sensitive or exposure-sensitive decision that deserves review before the daemon becomes ordinary background fact

AnonSync should not clone that shape.
A serious control surface should instead publish one bring-up and control-entry review model so “what exactly am I opening, under what continuity story, and how is control exposed?” becomes explicit product truth rather than installer folklore.

## Core rule

A non-trivial bring-up situation should always compile to a reviewed bring-up surface.
That includes at least:

- any host where startup is not obviously “fresh local-only state on this machine”
- any attach, import, recovery, or continuity-sensitive re-home where state identity, prior grants, or prior exposure may matter
- any first control entry that widens from local socket / loopback into reviewed LAN, SSH-forwarded, reverse-proxied, or other remotely reachable access
- any case where storage path, service profile, runtime user, or discovered root could cause the operator to administer a different durable state universe than expected
- any Linux/WebUI/headless path where the product would otherwise ask the operator to infer continuity or exposure from flags, config files, or bind-address lore

A channel may compress the review when risk is truly low.
It may not replace the meaning with vague `init`, `start`, `open WebUI`, `apply key`, `attach root`, or `run with --config` prose.

## Entry points that must converge

The product may offer several ergonomic entry points:

- first-launch workbench `Review bring-up`
- system-state page `Prepare attach / recover / open control`
- recovery page `Open recovered state with review`
- CLI `bringup review --state new ...`
- CLI `bringup review --attach /srv/anonsync/root ...`
- CLI `bringup show <bringup_case_id> --view review`
- a daemon startup path that emits a bring-up case instead of silently opening ambiguous state

But these must all converge on the same public bring-up model.
The operator should never have to wonder whether one surface is just a friendly starter wizard while another is the only place that actually explains continuity, identity, and control exposure.

## Fixed review order

Every non-trivial bring-up review should render the same sections in the same order:

1. **Host role and runtime target**
2. **State and continuity choice**
3. **Identity and relationship posture**
4. **Control access and network posture**
5. **Blockers and bootstrap dependencies**
6. **Receipt promise**

### 1) Host role and runtime target

This section should show:

- whether the host is being prepared as workstation, background service, local-web appliance, recovery bench, or inspect-only station
- which runtime / service profile is intended
- whether the chosen runtime stays local-only, expects a browser/workbench, or is preparing headless automation
- whether the trigger came from fresh start, attach, import, recovery, profile switch, or startup interception

The operator must be able to answer: **what role is this host about to play, and which runtime posture am I choosing?**

### 2) State and continuity choice

This section should show:

- whether the operator is creating fresh state, attaching known state, importing state, consuming recovery material, or performing successor-sensitive continuity work
- candidate state-root path or artifact, when applicable
- whether the choice preserves the same durable identity universe, opens a different one, or is still unresolved
- whether the action is ordinary local initialization, reviewed continuity, or blocked pending stronger proof

The operator must be able to answer: **am I opening the same state, a new state, a recovered state, or a continuity-sensitive replacement?**

### 3) Identity and relationship posture

This section should show:

- whether identity posture is new, retained, imported, successor-bound, or inspect-only
- whether existing constellation membership, remembered approvals, or grants would become active if bring-up succeeds
- whether the current bring-up remains relationship-neutral until later review
- whether a discovered state root or recovery bundle carries unexpected identity or relationship consequences

The operator must be able to answer: **which identity and relationship consequences become real if I continue?**

### 4) Control access and network posture

This section should show:

- whether control starts as local socket only, loopback workbench, SSH-forwarded, reviewed LAN, reverse-proxied, or another explicit posture
- which endpoint(s) will listen, on what address or class, and with what trust boundary
- whether discovery/publication defaults or known-host-only posture are being installed at first entry
- whether widening control exposure is bundled with state open or requires a separate reviewed step

The operator must be able to answer: **how will I reach control, and what network or disclosure posture am I creating right now?**

### 5) Blockers and bootstrap dependencies

This section should show:

- missing permissions, unsupported or stale roots, unavailable interfaces, recovery-material gaps, platform deprecations, or other hard blockers
- whether the blocker is local-host-specific, runtime-profile-specific, artifact-specific, or exposure-specific
- whether the honest next step is verify root, narrow exposure, gather recovery material, choose a different role, or stop
- whether the case is blocked, guarded, or ready

The operator must be able to answer: **what still prevents safe bring-up, and what must happen before this becomes ordinary startup?**

### 6) Receipt promise

This section should show:

- which bring-up receipt will exist after apply, defer, or rejection
- what it will later prove about host role, chosen continuity story, identity posture, accepted control exposure, and unresolved follow-up
- whether the receipt remains provisional because verification or exposure changes are still pending
- what later audit survives if the operator later changes runtime, narrows exposure, or performs successor cutover

The operator must be able to answer: **what later evidence will prove how this host was first opened and under what control posture?**

## Action hierarchy inside bring-up review

The primary action should be the safest meaningful next step.
Examples:

- fresh workstation with local-only control → `Create local-only state`, not `Start syncing`
- discovered prior root with uncertain integrity → `Verify and inspect root before opening`, not `Launch daemon`
- recovery bundle with continuity implications → `Prepare reviewed recovery attach`, not `Import now`
- reviewed LAN control request on a headless host → `Prepare LAN exposure with receipt`, not `Open WebUI`

Convenience labels such as `Get started`, `Open UI`, `Run with config`, or `Start daemon` should be visually separate and usually not primary.

## What the surface must never imply

The bring-up surface must never imply that these are the same thing:

- fresh initialization versus reopening known durable state
- attach/import/recover versus successor-sensitive continuity
- local-only control versus reviewed remote-reachable control
- runtime role choice versus mere cosmetic startup preference
- blocked prerequisites versus harmless post-start tuning
- unsupported clone-style copying versus supported continuity or recovery work

## Cross-links to other review models

Bring-up review should often hand off to nearby review families, but it should not dissolve into them.

- **State-root review** answers which root exists and how transitions behave.
  Bring-up review answers what opening that root means right now.
- **Control-access review** answers durable endpoint/session/token posture.
  Bring-up review answers what first control entry is being created as the host comes alive.
- **Recovery review** answers what material exists and what it can preserve.
  Bring-up review answers what happens when that material is actually consumed into live state.
- **Successor cutover review** answers continuity-sensitive replacement at broader scope.
  Bring-up review answers whether current startup is ordinary attach or the front door to that stronger review.
- **Release review** answers compatibility/channel boundaries.
  Bring-up review answers whether those boundaries block or narrow this actual first open.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync bringup show <bringup_case_id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether startup is fresh, attached, recovered, successor-sensitive, locally contained, remotely exposed, or blocked.

## Linux/headless parity rule

A Linux-first product has to assume that first control entry frequently happens over SSH, WebUI, or automation.
So the reviewed bring-up grammar must survive across those channels.
It is not acceptable for one richer surface to show host role, continuity, identity, exposure, and blockers while Linux/headless falls back to startup flags, bind-address lore, storage-path memory, or activation ritual.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed bring-up grammar is how the archive avoids rebuilding a system where service mode, storage path, identity creation, exposure choice, activation, and unsupported clone warnings are all individually documented, yet the full meaning of “what exactly am I opening, under which continuity story, and how is control exposed?” still depends on which installer page, config file, or support article the operator happened to notice first.
