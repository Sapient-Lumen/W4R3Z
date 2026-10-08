# Resilio seat lineage, identity replacement, and reset-boundary evaluation

## Why this pass exists

The archive already had strong doctrine for grants, approvals, linked-seat scope, and recovery.
What it still lacked was one direct current Resilio evaluation for another ordinary seam:

> when an operator resets credentials, links a second running install, hides an offline row, moves into service mode, or repairs a corrupted mobile identity, where does the product itself own the answer to `is this still the same seat?`, `did I just replace identity?`, `is this duplicate row harmless residue or a second live seat?`, and `what continuity did this reset actually preserve or destroy?`

Current official Resilio docs still show a useful, living product, but they also still show that ordinary seat-continuity truth leaks across several different article families at once:

- identity / linking guidance
- hide-offline-device guidance
- password-reset guidance
- Windows service install and service troubleshooting
- uninstall / cleanup guidance
- mobile identity-corruption recovery guidance

## Current official Resilio evidence that matters here

Current official docs still show an active v3 line through `3.1.2.1076`.

They also still say all of the following:

- Each Sync installation gets its own digital certificate and fingerprint; the fingerprint is part of how other peers recognize which installation is connecting.
- If two devices already running Sync are linked together, one can lose its certificate and take over the certificate of the other; when that happens, Advanced folders on the acquiring device are removed from the app and folders from the other instance are copied.
- Unlink is only local; the docs still explicitly say you cannot remotely unlink other devices.
- Clearing an offline device does not unlink it; it only hides the row, and the row can reappear later if that device comes back online.
- One documented WebUI password-reset path still duplicates the device in `My devices` and resets global preferences, while the config-file path avoids both of those side effects.
- Service migration on Windows still distinguishes `migrate settings` from `clean installation`; the clean path requires re-share and reconnect work.
- Running the service as `Local System` can produce the welcome screen with no old folders visible because Sync created a different storage folder, after which the operator must re-add and re-share / reconnect folders.
- On Android, error 205 still means the current identity is corrupted and cannot be replaced with a new one until the device is unlinked and re-created locally.

So current Resilio still contains a real but scattered answer to `did I preserve the same seat, and what exactly changed?`

## What Resilio still gets right

### 1) It treats seat identity as certificate-bearing, not as a friendly label only

Current docs still make the installation fingerprint real.
That is good.
A sync product should not pretend that device name alone is enough to reason about trust continuity.

### 2) It is honest that some recovery paths are not neutral

The password-reset article still plainly says that one reset ritual duplicates device rows and resets global preferences, while another avoids those effects.
That honesty is valuable.
A weaker product would hide those side effects until after the fact.

### 3) It distinguishes clean install from migrated continuity

The Windows service guidance still admits that `migrate settings` and `clean installation` are materially different continuity choices.
That is exactly the right instinct.

### 4) It admits that hidden device rows are not gone

The offline-device article still says hiding does not unlink and that the row may return.
That is useful because it refuses to confuse roster cleanliness with revocation.

## Why this is still a good reason not to clone them

### 1) Seat lineage is still not one product-owned truth surface

The operator still has to cross-read several current docs to answer one ordinary question:

- is this the same seat as before?
- did I just take over another seat's certificate?
- is this duplicate row a new live seat, a harmless reset artifact, or stale residue?
- did this reset preserve folders, settings, identity, or only local bytes?
- is this row merely hidden, actually unlinked, or only offline?

That is exactly the sort of ordinary question AnonSync should answer on one stable page family.

### 2) Identity replacement is still too easy to discover only after damage

Current docs do warn that linking two already-running devices can replace one certificate and remove Advanced folders from the app.
That warning matters.
But the ordinary interface contract still leaves too much of the takeover meaning implicit.
AnonSync should force a reviewed `identity replacement` page before anything destructive crosses that line.

### 3) Roster residue and live duplicates are still too easy to blur together

Current docs still show several reasons the device list can contain confusing rows:

- hidden but not unlinked
- duplicated through one credential-reset ritual
- offline because the installation was removed
- replaced by a fresh storage-root/service-world seat
- genuinely live and returning later

That is a strong reason to replace the roster contract instead of cloning it.

### 4) Reset and rehome impact is still split across support prose

Current docs still spread the answer to `what continuity survives this reset?` across password-reset docs, service-install docs, troubleshooting, uninstall cleanup, and mobile identity repair.
AnonSync should keep the honesty but collapse it into one exact impact page.

## What AnonSync should borrow directly

- certificate / fingerprint as real seat identity evidence
- honesty that reset paths have materially different side effects
- explicit distinction between migrated continuity and clean install
- explicit distinction between hidden roster rows and actual unlink / retirement

## What AnonSync should adapt instead of clone

### 1) Seat lineage must be its own page

The product should expose one page that answers:

- same seat
- successor seat
- foreign seat
- replaced seat
- stale roster residue

The operator should not infer lineage from row names, path accidents, or support notes.

### 2) Identity replacement must be its own page

Any operation that would cause certificate takeover, subject removal from the app, or new-family import should go through a destructive review page before commit.

### 3) Device roster interpretation must be its own page

Roster rows should explicitly classify whether they are:

- live current seat
- offline but still linked
- hidden residue that may return
- duplicate artifact from reset or rehome
- replaced successor pair
- stale row awaiting retirement decision

### 4) Reset / rehome impact must be its own page

Before apply, the product should say exactly what survives and what does not:

- local bytes
- durable identity
- linked relationships
- subject bindings
- preferences / policy
- credential surface
- roster rows on peers

## Resulting replacement pages

This pass therefore adds four more ordinary page contracts:

1. **Seat lineage** — same seat, successor seat, or foreign seat verdict
2. **Identity replacement** — certificate takeover, subject loss, and safe-link review
3. **Device roster** — hidden offline, duplicate, and returning seat interpretation
4. **Reset impact** — reset path, storage rehome, and preservation verdict

## Bottom line

Current Resilio docs still show a serious product with practical recovery and linking behavior.
That is exactly why the comparison matters.

The stronger AnonSync line is now:

> borrow Resilio's certificate-backed seat identity and its honesty about reset side effects, but refuse any interface contract where `same seat`, `replaced seat`, `hidden row`, and `fresh storage-root world` remain truths the operator must reconstruct from several support articles.
