# Resilio diagnostic-lane activation, self-serve support boundary, and evidence-residue fragmentation evaluation

## Why this pass exists

The archive already had serious work on diagnostics, evidence plans, telemetry consent, and export review.
What the latest revision chain still lacked was one tighter current Resilio pass about a more ordinary operator question:

> when I turn diagnostics on, what exact capture family is active, who can actually receive the result, what local residue does that leave behind, and what stronger support sentence is still blocked?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `Collecting debug logs manually` and `Collecting debug logs automatically` still say direct technical support is available only for Resilio Sync Business customers, while Sync v3 users are steered toward the forum and Help Center.
- those same current guides still say debug logging can be enabled from Settings/Preferences or through a `debug.txt` file containing `FFFFFFFF` in the storage folder, that Sync should be restarted to make sure logging is enabled, and that logs should collect for at least 15 minutes after reproduction.
- the manual guide still says logs are `sync.log` plus rotated `sync.log.<number>.zip`, still names platform- and service-user-specific storage locations, and still says only 20 MB attachments are allowed before a larger upload link is needed.
- `Increasing Debug Log size` still says `log_size` defaults to 100 MB, rotates `sync.log` into `sync.log.old`, can consume up to `log_size * 2` locally, and cannot be adjusted on mobile platforms.
- `Power user preferences` still keeps `send_statistics`, `log_size`, `log_ttl`, and `profiler_enabled` distinct, and still says profiler data is stored as `profiler.dat` in the storage folder, rotated every 10 minutes, and requires restart to activate.
- `Collecting crash reports, mini-dumps and core dumps` still treats crash reports, minidumps, and core dumps as different artifact families with different paths by platform and Windows service user.
- `Collect debug logs on mobiles` and `Settings on mobile platforms` still say mobile debug capture has its own hidden flow, including `SNC.DBG.LOGS`, hidden `.synclogs`, and Android cleanup that clears residual files as well as current debug logs.

That is a good reason to keep studying Resilio.
It is also another good reason not to clone the exact interface contract.

## What current Resilio still gets right

### 1) It admits that diagnostics are not one toggle

Current docs still preserve real differences among:

- anonymous statistical metrics
- debug logs
- profiler traces
- crash artifacts
- automatic send lanes
- manual attachment or upload lanes
- mobile-only extraction rituals

That honesty is useful.

### 2) It admits that support entitlement is not universal

Current guides still clearly distinguish:

- staffed vendor support lane for Business
- self-serve forum/help-center lane for Sync v3
- payment or licensing web-form lane

That is much better than pretending every user has the same escalation path.

### 3) It admits that local evidence has cost and residue

Current docs still say log rotation size matters, TTL matters, profiler output persists locally, crash dumps live in platform-specific places, and mobile cleanup is a separate act.
That is contract-shaping truth, not implementation trivia.

## Why AnonSync still should not clone it

### 1) One ordinary answer still spans too many pages

To answer `what evidence am I collecting now and who can I honestly send it to?` the operator may still need to combine:

- manual debug logging
- automatic debug logging
- mobile debug logging
- debug-log size tuning
- power-user preferences
- crash dump collection
- mobile settings

That is too much archaeology for one ordinary decision.

### 2) `Enable debug logging` still compresses too many separate truths

That one toggle can hide:

- capture family
- restart requirement
- hold-time sufficiency
- local rotation budget
- support-lane entitlement
- send route
- crash-artifact non-equivalence
- cleanup residue

AnonSync should not inherit that compression.

### 3) evidence send still feels procedural rather than contractual

Current Resilio docs still make the operator discover late that:

- a packet can be ready locally but unsupported by the current product/support lane
- a send route can be automatic, manual attachment, or out-of-band upload
- stopping capture is weaker than proving local residue is gone
- mobile extraction is not the same lane as desktop feedback submission

AnonSync should surface those truths in one reviewed family.

## Hard decisions for AnonSync

This pass freezes five decisions.

### Decision 1 — diagnostic lane is first-class product state

AnonSync should model at least these distinct families:

- **anonymous metrics lane**
- **debug capture lane**
- **profiler capture lane**
- **crash artifact lane**
- **outbound escalation lane**

### Decision 2 — capture, send, and cleanup stay separate

`collecting`, `ready to send`, `sent`, `retained locally`, and `cleaned up` must never collapse into one comforting `support package` noun.

### Decision 3 — support entitlement and disclosure route stay visible

If the current product line only supports self-serve or community guidance, the product must say that plainly instead of implying a staffed vendor lane.

### Decision 4 — restart and hold time are reviewed boundaries

A capture family that needs restart or a 15-minute window must publish those requirements before anyone treats the evidence as sufficient.

### Decision 5 — every diagnostic-affecting act emits one receipt

The receipt must preserve capture family, activation route, restart/hold-time boundary, outbound lane, residue class, and the blocked stronger sentence.

## Resulting page family

This tranche therefore adds five more first-class pages:

- **Diagnostic lane contract sheet**
- **Debug capture review**
- **Crash and profiler custody page**
- **External support lane proof**
- **Diagnostic lane lineage receipt**

## The non-clone line

The tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that anonymous metrics, debug capture, profiler traces, crash artifacts, staffed support, self-serve guidance, and cleanup residue are different truths. But it is not worth cloning the way the ordinary answers to `what am I collecting now`, `who can receive it`, `what has to happen before it is sufficient`, and `what still remains local afterward` still sprawl across several support articles instead of one stable page family.
