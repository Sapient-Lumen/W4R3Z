# Resilio capability gating, alert delivery, and kind chooser evaluation

## Purpose

The archive already has stronger answers for trust, typed intake, rate truth, byte posture, custody, lineage, observer visibility, state-root continuity, helper policy, and host cadence.
What still remained under-specified was another ordinary but load-bearing non-clone seam:

> current Resilio docs are fairly candid about capability limits, version-family caveats, platform-specific notifications, and different creation verbs — but the operator still has to reconstruct one coherent answer from licensing pages, FAQ pages, update guides, platform settings, permission docs, and separate sharing/backup articles.

This document tightens that line.
It does not argue that Resilio lacks real capability or useful workflows.
It argues that the capability truth is still spread across too many surfaces to earn direct interface cloning.

## Bottom line

Resilio still deserves credit here.
Current official docs still show all of the following are real and useful:

- capability and edition changes are documented explicitly instead of being hidden entirely
- current docs are candid that v3 requires activation, that non-commercial personal-device reuse is allowed, and that some older family combinations are risky or blocked
- current docs are candid that notifications depend on platform, settings, and OS permissions rather than pretending delivery is magical
- current docs offer several genuinely useful creation families: ordinary sync, advanced-folder sharing, single-file send, backup, encrypted custody, and local same-host shares

Those are good instincts.
But the same docs also show why AnonSync should not clone the page contracts.

## The four load-bearing non-clone seams in this pass

### 1) Right-to-run truth is still scattered across account, key, edition, and expiry articles

Current official docs still say all of the following at once:

- v3 requires a license to activate
- previously purchased Home Pro and Home Pro for Family continue to work
- new personal-use customers get a license from the site
- the same license may be used on several personal devices for personal non-commercial use
- the newer site-acquired personal license is associated with one person and cannot be shared outward
- some families such as local same-host shares stop working if trial or license expire or the license is removed

That is useful honesty.
It is still not one ordinary page answering:

> what capabilities does this seat actually have right now, where did those capabilities come from, which of them depend on remote/account state, and which will survive offline or expiry?

### 2) Compatibility and update-family truth is still article-shaped

Current official docs still say all of the following at once:

- v2 and v3 preserve synchronization compatibility
- linked devices should all be updated to v3 to avoid license conflicts
- Sync Business cannot be updated to v3, including personal Windows Server installations
- preserving the same storage/config/user context during update is important to preserve configuration and shares

That is good operational candor.
It is still not one ordinary page answering:

> if I mix these runtime families, editions, or storage roots, is the outcome safe, sync-only compatible, link-risky, or blocked?

### 3) Alert delivery is still surface- and permission-shaped instead of page-shaped

Current official docs still say all of the following at once:

- desktop preferences control whether approval/sync notifications are shown
- mobile settings separately control notifications and some network/background behavior
- Android permissions include push-message and wakefulness requirements
- Linux has no tray icon and notifications do not appear outside Sync UI

That is respectable honesty.
It is still not one ordinary page answering:

> if an approval request, warning, or completion event mattered, which carrier could actually deliver it on this seat, which gate could suppress it, and how do I recover after a miss?

### 4) Subject-kind creation is still menu-shaped rather than comparison-shaped

Current official docs still say all of the following at once:

- desktop sharing splits standard vs advanced folder dialogs and changes permission/approval semantics
- single-file sending has its own TTL and recipient workflow
- Android exposes `Send file`, `Create folder`, `Add backup`, `Scan QR code`, and manual key entry through `+`
- camera backup and Android backup create distinct retention and destination behavior
- local same-host shares and encrypted folders are separate families with their own platform/edition gates

Those are real capability families.
They are still not one ordinary page answering:

> what kind of subject am I about to create, what retention/authority/deletion contract comes with it, and why is this kind allowed here but another kind blocked?

## What AnonSync should copy

AnonSync should copy the useful parts more boldly:

- explicit capability families instead of pretending everything is one generic share
- candid compatibility fences instead of vague `may not work` folklore
- honest notification carrier limits
- practical creation verbs for send, backup, sync, encrypted custody, and same-host derivation

## What AnonSync should refuse to clone

AnonSync should refuse the exact current page contracts where:

- right-to-run depends on reading licensing, update, and platform docs together
- compatibility truth depends on mentally merging sync compatibility, link compatibility, and edition-family restrictions
- alert delivery truth depends on preferences, OS permission pages, and platform caveats with no single carrier matrix
- creation meaning is hidden in whichever menu entry or platform article happened to be used first

## The replacement pages this revision adds

This revision therefore adds four ordinary replacement pages:

1. **Capability source** — what capabilities this seat has, where they came from, and what remote/expiry dependence remains
2. **Compatibility gate** — whether the contemplated join/update/mix is safe, sync-only compatible, risky, or blocked
3. **Alert delivery** — which carrier could actually deliver the event, which gate could suppress it, and how recovery works after a miss
4. **Subject kind chooser** — what each creation kind means before the operator commits to it

## Result

The Resilio stance is now tighter again:

> borrow the capability families and the candor; refuse the article-scattered page contracts; replace each refusal with one ordinary page that makes the operator answer local, exact, and reviewable.
