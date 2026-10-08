# Resilio surface-capability parity and browser-handoff gap evaluation

## Why this pass exists

The archive already had stronger doctrine for browser control, import fallback, and channel parity.
What it still lacked was one direct current Resilio evaluation for a narrower seam:

> when the operator is already in a surface and asks `can I do this here right now?`, where does current Resilio actually answer that question?

This is where the non-clone reason becomes tighter.
Current official Resilio docs still make the product look competent and alive, but they also show that ordinary action truth still leaks across browser behavior, surface kind, role caveats, and troubleshooting pages.

## Current official Resilio evidence that matters here

Current official docs still show an active v3 line through `3.1.2.1076` in late 2025, including UI work in WebUI-adjacent areas.
They still show browser/local-web control as ordinary on Linux and on Windows service installs, with loopback defaults unless widened deliberately.
They also still show a practical share dialog with link, QR, e-mail, and clipboard delivery, plus an ordinary browser-open path where the default browser may ask permission to launch the Sync app. 

But the same current docs also still say:

- opening a shared link in a browser is impossible when Sync is being accessed through WebUI, so the operator must fall back to `+` → `Enter a key or link`
- a missing Share button in WebUI can be caused by browser incompatibility or ad-block software rather than role or policy alone
- advanced-folder sharing can disappear legitimately because only Owners may share
- some service/local-web actions still depend on whether the current listener is loopback-only versus widened

So the answer to `why is this action missing or broken here?` still does not belong to one stable product-owned page.

## What Resilio still gets right

### 1) Browser-first local control is still the right instinct

Resilio is still right that Linux-heavy and service-heavy seats need browser/local-web control as a first-class path.
AnonSync should not retreat from that.

### 2) Carrier flexibility is still genuinely useful

Resilio is still right that the same share family may need link, QR, e-mail, browser-open, and manual paste paths.
The operator benefit is real.

### 3) The docs are candid about some awkward realities

Resilio's docs do not pretend every fast path is universal.
They explicitly say when WebUI cannot consume direct-link opening, when a browser may need to launch an external app, and when a browser or ad blocker can interfere with WebUI affordances.
That candor is useful.

## Why this is still a good reason not to clone them

### 1) Current-surface capability truth is still scattered

Resilio still makes the operator reconstruct one ordinary answer from several places:

- the share dialog for what should be possible
- the desktop guide for browser-open behavior
- the browser-link troubleshooting page for why that fast path failed
- the WebUI exception for why the same link cannot be consumed there
- the missing-Share-button article for browser/ad-block interference
- role caveats for why some absence is legitimate rather than broken

That is too much archaeology for one ordinary question.

### 2) Surface mismatch and artifact mismatch are still easy to confuse

Current docs still leave several distinct states close together:

- the artifact is fine, but this surface cannot consume it
- the artifact is fine, but the browser blocked the handoff
- the action exists, but browser/ad-block rendering hid the affordance
- the action is actually unavailable because the current peer lacks Owner rights
- the current runtime is healthy, but the current projection cannot complete the work

These are different truths.
A product should not ask the operator to infer which one applies from a mix of absent buttons, browser prompts, and help pages.

### 3) `Try another client` is still too close to the practical answer

Resilio's fallback is not wrong.
Manual paste is real and useful.
But the product contract is still too thin when the strongest answer is effectively `open another lane and do it there` without one page proving whether the operator is continuing the same work or starting a semantically different path.

### 4) Browser/app ergonomics still risk becoming hidden policy

When browser choice, protocol-handler permission, ad-block status, or surface kind materially changes the answer to `can I do this here?`, the interface contract is not strong enough.
The product must name those factors explicitly instead of letting them masquerade as product authority.

## The tighter AnonSync conclusion

AnonSync should borrow the following from Resilio more boldly:

- browser-first local control
- link / QR / manual carrier flexibility
- explicit acknowledgment that some fast paths depend on browser or OS cooperation

But AnonSync should refuse the exact page contract whenever one ordinary action answer still depends on:

- browser-launch prompts
- remembered protocol-handler permission
- current surface mismatch
- ad-block or browser-render interference
- role caveats that look too much like broken UI
- manual fallback that is semantically correct but insufficiently explained

## The replacement pages this evaluation justifies

This pass therefore makes four page-shaped obligations concrete:

1. **Action availability** — is the action actually supported here, inspect-only, handoffable, blocked by policy, or broken by the current surface?
2. **Surface mismatch** — what exactly mismatched: direct-link support, protocol registration, browser blocker, role, policy, or artifact health?
3. **Review handoff** — if the work must move channels, how is the current reviewed subject/gate/draft preserved?
4. **Resume action** — did the target channel really continue the same reviewed action, or reopen broader review?

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that browser-first control and carrier-flexible sharing are worth building, but it is also current evidence that ordinary action truth still leaks across browser behavior, surface kind, and troubleshooting pages. AnonSync should copy the practicality and refuse the page contract.
