# Resilio surface parity, external edit, background delivery, and mobile storage evaluation

## Purpose

The archive already has stronger answers for shell acceleration, alert delivery, host cadence, path continuity, and repair ladders.
This document asks a narrower but still ordinary question that current Resilio docs keep making visible:

> when the same subject is opened, edited, cleared, backgrounded, or inspected from desktop, Linux/WebUI, Android, and iOS, where does the product itself own one stable answer, and where does the operator still have to remember platform folklore?

This is not a complaint that Resilio ignores platform reality.
It does not.
The problem is that the ordinary operator answer still leaks across too many platform-specific articles.

## Current Resilio evidence that matters

Current official docs still show all of the following at once:

- Linux has no OS integration, no tray icon, and no notifications outside Sync UI.
- Linux sharing, license-seat links, and activation still route through `Enter a key or link`, and WebUI remains the ordinary control surface there.
- Desktop can keep syncing while the window is hidden, Linux can run headlessly through WebUI, Android can run in the background but may still be stopped by task killers, auto-sleep, battery saver, or forbidden-network policy, and iOS cannot transfer data in the background.
- iOS `Open In...` editing works on a copied file, not a live bind; to propagate changes the edited copy must be sent back into Sync.
- iOS deletion from the local app can simply un-sync the file locally rather than issuing a global delete.
- Android share details expose path, archive toggle, relay/tracker/LAN/known-host settings, and `Clear` versus `Disconnect`, while iOS exposes a different but overlapping share-details grammar.
- iOS keeps files in its sandbox; storage accounting splits app data from user data; clearing local material depends on Selective Sync being enabled.
- iOS shared-link history, download retention, and on-device file presence still split between `Downloads`, `Shared links`, and the broader storage page.
- Android `Simple Mode` hides path/root choice and forces new shares into `Downloads/Sync`, while disabling it restores explicit location choice.

These are all useful facts.
The problem is that they still do not add up to one stable product-owned answer for ordinary cross-surface behavior.

## Where Resilio is genuinely good

### 1) It admits that surfaces are not equivalent

Resilio does not pretend that desktop shell, Linux/WebUI, Android, and iOS all expose the same verbs.
That honesty is good and AnonSync should keep it.

### 2) It is candid about iOS copy semantics

The iOS docs plainly say that external-app editing happens on a copy and that the edited file must be sent back.
That is much better than implying a live document bind that does not exist.

### 3) It is candid about background limits

The docs are also straightforward that Android background delivery is contingent, iOS background delivery is unavailable, and Linux headless control is WebUI-shaped.
AnonSync should keep that candor.

### 4) It exposes local-storage pressure as a first-class reality on mobile

Resilio still makes Selective Sync, placeholder clearing, sandbox storage, and share-specific downloads real user concepts instead of pretending that mobile storage is infinite.
That is useful and worth borrowing.

## Why this still does not earn cloning

### 1) The ordinary surface answer still fragments by platform article

A user asking `can I do this here?` still has to assemble the answer from Linux peculiarities, Android interface pages, iOS interface pages, background notes, and edit/storage peculiarities.
That is not one stable page contract.

### 2) External edit semantics still live in specialist lore

The iOS `copy out, edit elsewhere, send back` contract is honest, but it is not owned by a universal action page that would naturally explain `open`, `edit`, `save back`, and duplicate risk.

### 3) Freshness expectation is still scattered across background, battery, network, and task-killer notes

The operator still reconstructs `will this keep receiving updates while I am away?` from separate platform behavior notes rather than one page publishing current background eligibility and suspend gates.

### 4) Mobile storage truth is still split across multiple surfaces

On iOS in particular, the operator still needs several pages to answer:

- where the bytes physically live
- what counts as app data versus user data
- what `Clear synced files` or `Remove from this device` actually removes
- which things remain in history after local removal
- whether a removed local copy is reacquirable later

### 5) Surface asymmetry still leaks into creation and path choice

Android `Simple Mode`, iOS sandboxing, Linux WebUI, and desktop shell affordances all shape where work begins and what verbs are visible, but those facts still are not gathered into one surface-capability answer.

## What AnonSync should borrow

AnonSync should borrow all of these ideas:

- surface-specific capability honesty
- explicit copy-versus-live-bind edit semantics
- background-delivery candor with named suspend reasons
- mobile storage accounting and placeholder-based clearance
- explicit network and battery gates for delivery on constrained devices
- per-surface fallback paths when a stronger affordance is unavailable

## What AnonSync should refuse to clone

AnonSync should refuse these interface shapes:

- letting capability truth live mainly in platform-specific help pages
- hiding copy/export/save-back semantics inside one platform tutorial
- treating background freshness as a generic `online/offline` badge
- scattering local-storage truth across downloads, settings, and share-detail surfaces without one ordinary storage page
- letting creation/path-picking differences remain side effects of hidden simple-mode or sandbox assumptions

## The replacement page family this evaluation now requires

This pass therefore adds four more ordinary pages:

1. `309-surface-capability-page-action-parity-and-reason-coded-gaps-interface-spec.md`
2. `310-external-edit-review-page-copy-bind-saveback-and-duplicate-risk-interface-spec.md`
3. `311-background-delivery-page-suspend-gates-freshness-floor-and-catchup-risk-interface-spec.md`
4. `312-mobile-storage-page-sandbox-clearance-downloads-and-reacquireability-interface-spec.md`

The sharpened line is now:

> when Resilio keeps cross-surface truth honest only by spreading it across Linux/WebUI peculiarities, Android settings, iOS edit/storage caveats, and background notes, AnonSync should copy the honesty and replace the pages.
