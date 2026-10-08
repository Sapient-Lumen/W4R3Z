
# Resilio control-surface bootstrap, exposure, and recovery evaluation

## Purpose

The archive already had control-trust, install-readiness, artifact-intake, and credential-recovery doctrine.
What it still lacked was one explicit comparison document for another ordinary seam:

> when the operator asks `what control surface am I actually using, who can reach it, why does the browser distrust it, and how do I recover access without side effects?`, where does the product itself own the answer?

Current official Resilio docs are candid enough that AnonSync needs a serious answer.
Resilio does not completely hide the mechanics.
It says WebUI is the default path on Linux and on Windows service installs.
It says the listener is loopback-only by default, and it names the exact ways to widen it.
It says browser warnings can be bypassed temporarily or fixed durably.
It says one password-reset method duplicates the device row and resets global preferences, while another avoids those side effects.
That honesty is worth borrowing.

## What Resilio gets right

Resilio is still right that:

- browser-first local control is practical for Linux-heavy, NAS, and service-heavy installs
- exposure scope is not trivial; loopback-only and LAN-reachable are materially different states
- browser distrust is a real operator event rather than an ignorable cosmetic nuisance
- control recovery can have broader side effects than merely changing one password
- browser-open handoff failure and artifact invalidity are not the same problem

That is better than products that pretend local web control, browser warnings, and access recovery are self-explanatory.

## What current official docs still show

Current official docs still show all of the following are live product truths:

- Resilio Sync still has an active v3 line, with `3.1.2.1076` listed on `31/Oct/2025`
- WebUI is the default control path on Linux and on Windows when Sync is installed as a service
- the local web listener defaults to `127.0.0.1`, and widening it to `0.0.0.0` is a deliberate step rather than a silent default
- browser-warning recovery can involve a one-time unsafe proceed path, HSTS/cache clearing, or supplying a trusted certificate in config mode
- deleting `settings.dat` and `settings.dat.old` resets WebUI credentials but also resets global preferences and can duplicate the device in `My devices`
- a configuration-file method can set login/password without those duplicate-device or preferences-reset side effects
- opening share links in the browser can fail for browser/OS reasons, and WebUI itself cannot consume the direct-link path, forcing manual paste through `+ > Enter a key or link`
- SmartScreen or other OS trust gates can still interrupt installation even when the operator intends to use the product immediately afterward

That is enough to prove Resilio still solves real work.
It is also enough to show why AnonSync should not clone the page contract.

## What still should not be cloned

The page contract is still scattered.
Current official docs still require the operator to combine at least five article families:

1. **Configuring WebUI / Linux / service docs** for where control lives, what interface it binds, and how exposure widens
2. **Browser warning docs** for what distrust means and how to bypass or repair it
3. **Password-reset docs** for which recovery ritual preserves state and which one duplicates seats or resets preferences
4. **Link-open troubleshooting docs** for why browser-open handoff can fail and what fallback still works
5. **Installer / SmartScreen docs** for package trust and first-open blockers

That means one ordinary answer is still reconstructed from several places:

- what surface am I actually talking to?
- who can currently reach it?
- why is the browser distrusting it?
- is the current repair temporary or durable?
- what side effects happen if I recover control this way?
- which import fast paths are unavailable from this surface and what typed fallback remains?

The product substance is good.
The page ownership is still too weak.

## Why this matters for AnonSync

AnonSync should not repeat two common mistakes here:

1. **control by ritual** — treating browser warnings, bind strings, config snippets, and password-reset file deletion as the real explanation layer
2. **recovery by collateral damage** — letting lost control credentials silently widen into seat duplication, preferences reset, or unclear session invalidation

A serious sync product needs one stable public answer to four different questions:

- **surface truth** — what control surface is this, which runtime owns it, and what it can honestly do from here
- **exposure truth** — who can reach this listener now, and what happens if the bind disappears or widens
- **trust-repair truth** — why the browser distrusts this endpoint, what one-time exception does, and what durable fix is available
- **recovery truth** — how to regain access while preserving seat continuity and making any broader reset explicit

## Replacement pages in this revision

This revision adds four fixed pages:

- `362` — Control launch
- `363` — Control listener
- `364` — Browser trust recovery
- `365` — Control access recovery

Together they replace article-shaped control rituals with product-owned control truth.

## The doctrinal line

Borrow directly:

- browser-first local control as a first-class mode
- explicit loopback-by-default posture
- explicit acknowledgement that listener widening changes who can reach the daemon
- explicit acknowledgement that one recovery method can preserve state better than another

Do not clone directly:

- relying on browser chrome to explain trust state
- relying on config snippets to explain exposure scope
- relying on filesystem deletion rituals to recover access
- relying on generic `paste the link instead` fallback without naming surface/handler mismatch
- relying on OS-installer warnings and post-install folklore as the real control-entry story

## Conclusion

The correct AnonSync response is not merely `use a browser too`.
It is stronger than that:

> keep browser-first control, but make every local-web entry, listener mutation, browser warning, and control-secret reset resolve into one stable explanation surface that says what endpoint you are using, who can reach it, why the browser distrusts it, what repair is temporary versus durable, what fast paths are unavailable here, and what continuity is preserved after recovery.
