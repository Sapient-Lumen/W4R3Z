# Resilio control-surface grade, audience, auth, and transport fragmentation evaluation

## Why this pass exists

The archive already had strong pages for control launch, listener reach, browser trust recovery, and control access recovery.
What it still did not own cleanly enough was one ordinary operator question that appears before any of those deeper repairs:

- what grade of control surface am I actually using right now
- who can reach it
- what transport truth protects it
- what auth floor currently guards it
- what fallback or recovery route exists if this grade is weaker than I expected
- what stronger sentence is unsafe to claim

Current official Resilio docs still make that seam real.
They are candid that WebUI on Linux and Windows service installs defaults to loopback, that LAN reach requires widening the listen address, that workstation password setup is optional while NAS requires credentials, that HTTP is still the default transport, that HTTPS uses a self-signed certificate unless you provide your own certificate in config mode, that browser bypass / HSTS-clearing workarounds still appear in the support story, that cookies last only for the browser session, and that one password-reset path still requires deleting settings files in the storage folder with broader side effects than the config-file path.

That candor is useful.
The problem is that the operator still has to reconstruct one ordinary answer from several articles:

> what control-surface grade is this endpoint actually providing right now, and what stronger claim would be dishonest?

## What current Resilio still gets right

Current official docs still publish several operational truths worth borrowing.

- **Audience is materially real.** Current WebUI and Linux docs still say loopback-only is the default posture and LAN reach requires widening the listen address to all interfaces or another chosen interface.
- **Auth floor is named, even if loosely.** Current WebUI docs still say password setup is optional for workstations and compulsory for NAS, and session cookies last only until the browser session ends.
- **Transport truth is admitted.** Current WebUI docs still say HTTP is the default and HTTPS requires configuration.
- **Certificate trust is materially separate from transport enablement.** Current browser-warning docs still say HTTPS commonly presents a self-signed certificate that browsers do not recognize unless you bypass, clear browser residue, or install your own certificate.
- **Custom trust posture exists.** Current config-mode docs still support supplying a certificate and private key, plus password hashes, in configuration.
- **Recovery methods are not equal.** Current password-reset docs still say deleting settings files resets global preferences and duplicates the device row, while the config-file method avoids that collateral delta.
- **Control modality can silently narrow.** Current config-mode docs still say declaring shared folders in the config file disables WebUI altogether.
- **The current v3 line is still live.** Official docs still show the v3 line through `3.1.2.1076` dated 31/Oct/2025.

That is strong candor.
Resilio is still willing to admit that control-surface grade is not just decoration.

## Where current Resilio still stays too article-shaped

### 1. Grade still depends on operator archaeology

The ordinary operator should not have to reconstruct from memory whether the current control surface is:

- `loopback-only + passwordless + http`
- `loopback-only + passworded + http`
- `lan-reachable + passworded + http`
- `lan-reachable + https + self-signed`
- `lan-reachable + https + trusted cert`
- `headless config-controlled + no live WebUI`
- `browser-blocked but endpoint otherwise healthy`

Current Resilio still tells those truths, but it still makes the operator stitch them together from WebUI, Linux, browser-warning, config-mode, and password-reset pages.

### 2. Exposure, auth, and transport still blur into one `WebUI` noun

These are materially different realities:

- the browser is talking to localhost over HTTP
- the browser is talking across the LAN over HTTP
- the browser is talking over HTTPS but only under a self-signed trust exception
- the endpoint is configured with a trusted certificate
- the endpoint is recoverable only through config edits because live WebUI is disabled or unreachable

Those distinctions should be first-class product verdicts, not things inferred after a warning page or a failed login.

### 3. Recovery paths still hide control-plane side effects

The operator should not have to learn only after choosing a repair path that:

- deleting settings files resets broader preferences
- a password reset path can duplicate the device row in `My devices`
- config-enforced credentials are the lower-collateral path
- a transport warning may really be browser residue rather than endpoint identity loss
- enabling config-owned shares can disable WebUI and therefore move control to a different mode entirely

### 4. Intake parity still depends on surface memory

Current docs still say adding shares by clicking a link in the browser does not work with WebUI and manual `Enter a key or link` is required instead.
That means the product is still making the operator remember that the same artifact may redeem differently depending on surface and entry path.

## What AnonSync should do instead

AnonSync should make **control-surface grade** a first-class reviewed object.

The product should own four page families:

1. **Control-surface grade**
   - current audience scope
   - current auth floor
   - current transport / certificate posture
   - current control modality and fallback path
   - strongest safe sentence and stronger forbidden sentence

2. **Exposure/auth mutation review**
   - requested change in audience, auth, or transport
   - audience delta
   - browser / session consequences
   - any mode loss, restart need, or surface substitution
   - stronger claim blocked until durable trust exists

3. **Certificate posture and browser trust**
   - endpoint certificate origin and trust class
   - warning class
   - temporary bypass meaning
   - durable fix ladder
   - browser residue versus endpoint reality

4. **Control-surface receipt**
   - resulting grade after apply
   - audience/auth/transport verdict
   - control modality after apply
   - remaining residue or weaker claim floor
   - next safest recovery or hardening move

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that listener scope, workstation-vs-NAS password floor, transport choice, self-signed certificate posture, and credential-reset path materially change the effective control surface. But it is not worth cloning the way current operators still have to reconstruct, from several help articles, whether the current endpoint is merely local, broadly reachable, passwordless, self-signed, durably trusted, browser-blocked, or carrying hidden recovery side effects.

## New replacement pages added in this revision

- `572` Control-surface grade
- `573` Exposure/auth mutation review
- `574` Certificate posture
- `575` Control-surface receipt
