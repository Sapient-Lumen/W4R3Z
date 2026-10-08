# Resilio evaluation: stop proof, hidden runtime, and restart provenance fragmentation

Current official Resilio docs are still candid that `closed`, `stopped`, `hidden`, and `will start again` are not the same truth.
That candor is worth borrowing.
The page contract is still too fragmented to clone.

## Why this seam matters

A file sync runtime changes real-world consequences when it remains alive after the window disappears, when background work survives one projection but not another, when stop verbs differ across platform classes, or when the runtime can re-enter automatically at boot.
If the product does not own these distinctions, operators end up debugging ghosts: work that still runs after the UI vanished, work that stopped without a durable proof, or restarts that quietly alter chronology and evidence.

## What current official Resilio docs still distinguish well

Current official docs still preserve all of these as separate operational truths:

- Windows service mode can run regardless of whether any user is logged in and can run as `System`, `Local Service`, or current user.
- Desktop UI can be hidden or minimized while runtime work continues.
- Linux headless use can exist without an open browser projection.
- Android has an explicit `Exit` verb that is stronger than merely leaving the screen.
- Android background continuity can still be weakened by task killers and by turning notifications off, since lower priority may let background work stop.
- iOS background synchronization is unavailable.
- Mac/Windows expose `Start Sync on startup`, which is about future boot re-entry rather than present runtime state.
- Update/install guides still distinguish stopping a process, stopping a service, and re-launching with the same parameters and same user to preserve continuity.
- Shutdown and re-open can trigger re-indexing and change later overwrite chronology for offline edits.

That is strong semantic candor.
AnonSync should borrow it directly.

## Why the current contract still should not be cloned

Current official docs still make one ordinary operator answer depend on several article families.
To answer:

> did I actually stop synchronization, or did only one projection disappear while runtime work can still continue, restart later, or re-enter at boot?

an operator still has to merge:

- service-install and service-troubleshooting docs
- mobile interface docs
- mobile settings docs
- background-behavior docs
- startup preference docs
- update/install instructions

The distinctions are good.
The workflow ownership is still scattered.

## The AnonSync decision

AnonSync should make **stop proof** first-class product structure.
That means:

1. **projection close, background continuation, runtime stop, and future boot re-entry are separate modeled truths**
2. **a stop request is weaker than drain completion, and drain completion is weaker than no-further-publication proof**
3. **platform/runtime class must stay visible because hidden desktop runtime, Windows service runtime, Android runtime, and iOS foreground-only runtime do not share one stop contract**
4. **restart provenance stays visible because a later re-open can change indexing and chronology claims**
5. **every serious stop or re-entry action needs one receipt preserving request scope, residual work, auto-start posture, and the blocked stronger sentence**

## Replacement page family required

This seam adds five more product-owned pages:

- **Runtime stop contract sheet**
- **Shutdown drain review**
- **Runtime stop proof**
- **Restart provenance page**
- **Runtime stop lineage receipt**

## Strongest non-clone line

> Borrow Resilio's candor that service runtime, hidden desktop runtime, Android exit, notification-linked background priority, startup re-entry, and re-open chronology are materially different truths — but refuse any product contract where `close`, `stop`, and `won't come back` still require archaeology across service docs, mobile docs, settings, and update instructions.
