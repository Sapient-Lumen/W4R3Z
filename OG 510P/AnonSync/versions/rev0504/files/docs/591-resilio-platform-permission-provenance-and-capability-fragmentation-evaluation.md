# Resilio platform-permission provenance, denial fallout, and capability fragmentation evaluation

## Why this pass exists

The archive already had path grants, storage-class admission, capture-source pages, alert-permission pages, and runtime/profile work.
Those were necessary, but another current Resilio pass still exposes a more ordinary operator seam.
The problem is no longer only `can this folder path be written` or `does this seat have background support`.
It is now:

- what exact **OS/platform permission** is being asked for
- which exact **capability family** that permission unlocks
- what honest sentence the product can say if the permission is denied, later revoked, or only partially present on one platform family
- which degradations are **storage**, **camera/claim**, **background**, **network-visibility**, or **notification** narrowing rather than generic breakage
- what durable receipt proves the operator accepted, denied, or deferred that platform power

That seam is still materially real in current official Resilio docs.
They still document Android and Amazon Kindle permissions separately from mobile settings and mobile interface pages.
They still tie account access to identity-certificate generation and sending links / support mail, storage permission to writing received files, camera access to QR-based device/share connection, Wi-Fi/network info to interface and network awareness, boot permission to auto-start, wake-lock style permission to Auto-sleep activity checks, and platform messaging permission to connection-request notifications.
They also still document mobile settings where disabling notifications lowers Sync's system priority and may stop background work, and Android battery-saver / auto-sleep settings where the core can stop and peers stop seeing the device online.
The current v3 line still appears active through `3.1.2.1076`.

That is useful candor.
The non-clone problem is workflow ownership.
Resilio still leaves the ordinary sentence `why is the app asking for this, what becomes weaker if I deny it, and what exactly is still true afterward?` split across permission, settings, auto-sleep, and mobile-interface articles.

## What current Resilio gets right

Current official docs still deserve credit for saying plainly that platform permissions are not decorative.
They still connect permissions to real product powers:

- account / identity access can matter for certificate generation and share-link / support flows
- storage access is required to write received files and apply file changes
- camera access is used for QR-based device/share connection
- boot/startup permission backs auto-start
- wake-lock / prevent-sleep power backs Auto-sleep activity checking
- network-info and full-network permissions back sync traffic and network-state awareness
- messaging permission can back incoming approval / connection-request notifications
- notification settings can affect system priority and therefore background survivability

That is better than pretending OS prompts are generic plumbing.
AnonSync should keep that candor.

## What current Resilio still leaves fragmented

Current official docs still make the operator reconstruct one ordinary answer from several pages:

- `Permissions Sync requires on Android and Amazon Kindle` explains why permissions exist.
- `Settings on mobile platforms` explains Auto-start, Battery saver, Auto-sleep, network settings, and that disabling notifications lowers system priority and may stop background work.
- `Sync interface on Android` and `Sync Interface on iOS devices` explain which UI actions depend on camera scanning, share details, clear-to-placeholder, archive toggles, and network-per-share controls.
- `Configuring Auto Sleep & Battery Saver (Android)` explains that the core can stop, peers no longer see the device online, and wake-up intervals change behavior.

The operator therefore still has to do archaeology to answer a simple question:

> this permission prompt or denial appeared on my phone; what exact product power is involved, what is the real degraded state if I refuse it, and what stronger sentence must the product now forbid?

## Why this is a strong non-clone reason

This is not a cosmetic mobile-settings issue.
It changes claim ceilings and recovery advice.
Without a first-class permission-provenance object, the product can accidentally let operators say things that are stronger than the evidence supports, such as:

- `mobile sync is enabled` when storage write or network permission is absent
- `background syncing is broken` when the real issue is notification-priority downgrade or Auto-sleep policy
- `QR setup failed` when the real blocker is camera permission only
- `this seat is offline` when the core intentionally slept under battery policy
- `permission accepted means feature fully works` when another platform capability cliff still applies

All of those can be false for reasons the docs themselves already admit are real.

## Better product move for AnonSync

AnonSync should not clone a contract where platform permissions remain mostly OS-dialog lore plus scattered mobile help.
It should instead make **platform permission provenance** first-class.

That means every serious permission-bearing seat should publish, in one stable reviewed object:

- permission family
- capability families unlocked by it
- current grant state
- degraded-but-still-true sentence if absent
- stronger forbidden sentence
- next least-widening repair path
- receipt showing whether the operator granted, denied, deferred, or later revoked it

## New page family required

This pass therefore adds four explicit replacements:

1. **Platform permission provenance** — what OS/platform power is being asked for and why.
2. **Permission consequence review** — what exact capability narrows if granted, denied, or revoked.
3. **Permission request proof** — whether the prompt came from scan, storage write, startup, notifications, or another concrete product action.
4. **Permission state receipt** — durable safe language and aftermath.

## Condensed design verdict

Borrow Resilio's candor that platform permissions map to real powers such as storage write, QR connection, auto-start, background survival, and notifications.
Do not clone a product contract where operators still have to reconstruct permission meaning from security help, mobile settings, and battery-policy articles.
