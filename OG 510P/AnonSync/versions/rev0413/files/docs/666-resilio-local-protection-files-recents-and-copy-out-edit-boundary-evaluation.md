# Resilio local protection, Files-app visibility, and copy-out edit boundary evaluation

## Why this pass exists

The archive already had strong doctrine for mobile storage truth, subject-kind exceptions, non-authority edits, and cross-surface capability drift.
What it still lacked was one direct current Resilio evaluation for a narrower but important question:

> when a user says `protect this app` or `edit this file in another app`, does the product keep the local-privacy, OS-visibility, edit-lane, and recovery consequences adjacent, or does the operator have to reconstruct them from several mobile help pages?

Current official Resilio docs still show a useful, living product, but they also still show that one ordinary answer is spread across several article families at once:

- `Settings on mobile platforms`
- `Sync for iOS Peculiarities`
- `How to edit a document stored in Sync? (iOS)`
- `Storage Management on iOS`
- `Sync for Windows Phone Peculiarities`
- the still-live v3 line through `3.1.2.1076`

## Current official Resilio evidence that matters here

Current official docs still say all of the following:

- `Settings on mobile platforms` still says iOS `Touch ID & passcode` protects Sync and all files in it with a pin-lock, but once protected, Sync will no longer show those files in `Recents` inside the iOS Files app.
- The same current settings article still says Windows Phone passcode protection can create a recovery cliff: if the code is forgotten, the user cannot access Sync or synced files on that device and must reinstall the app, losing downloaded in-app data while other peers keep their copies.
- `How to edit a document stored in Sync? (iOS)` still says iOS apps cannot read files outside the application folder, so editing requires importing the document into another app and later putting the modified document back into Sync manually.
- The same current iOS editing article still says Sync cannot replace the original document with the modified one under iOS architecture, so the operator may see both the old and new versions unless they remove the original themselves first.
- `Sync for iOS Peculiarities` still says `Open In...` copies the file to the other app, that edits there do not change the file stored in Sync until the modified copy is sent back, and that deleting a file on iOS merely `un-syncs` it from iOS rather than issuing a delete to all peers.
- `Storage Management on iOS` still says Sync keeps files in its sandbox, separates `App data` from `User data`, and allows clearing local copies only when the share has Selective Sync enabled.
- `Sync for Windows Phone Peculiarities` still says opening a file in another app makes a copy, changes there do not affect the Sync-stored file until it is sent back, and deleting on the phone does not delete on other peers.

So current Resilio still contains a real but scattered answer to:

> is this file really protected, really editable in place, really visible to the OS, and really recoverable the way the toggle wording suggests?

## What Resilio still gets right

### 1) It is candid that mobile privacy and OS integration are not free at the same time

The docs do not pretend that `protect with passcode` is merely cosmetic.
They openly say that protection changes Files-app Recents visibility on iOS and can create a reinstall-and-local-loss recovery cliff on Windows Phone.
That honesty is valuable.

### 2) It is candid that outside-app editing is usually copy-return, not live in-place authority

The docs do not pretend that `open in another app` means the other app is editing the original synced object.
They openly say the file is copied into another app, edits there do not automatically affect the Sync copy, and the modified result must be sent back.
That candor matters.

### 3) It is candid that local mobile storage is app-shaped

The docs still say iOS keeps the files in Sync's sandbox, distinguishes service/app data from user data, and requires Selective Sync for certain local-clear operations.
That is real substrate truth rather than marketing prose.

## Why this is still a good reason not to clone them

### 1) `Protect this app` still hides an integration delta

Current docs still let one simple local-security control quietly stand in for several materially different truths:

- in-app access is now gated
- Files-app `Recents` no longer surfaces those files on iOS
- outside-app edit lanes may still be copy-return rather than live provider-backed editing
- on at least one mobile family, forgotten code can force reinstall and local-data loss

AnonSync should not inherit a model where a privacy toggle quietly changes OS visibility and recovery semantics without one product-owned review page.

### 2) `Edit in another app` still hides copy/branch semantics

Current docs still require the operator to learn from separate peculiarities and how-to pages that:

- the other app may receive a copy, not the authoritative live file
- Sync may not be able to replace the original automatically
- the operator may end up with old and new versions side by side
- only certain permission classes can return the modified file to the share

A serious sync product should not flatten `edit externally` and `edit in place` into one affordance.

### 3) Lock, visibility, and recovery are still documented as separate stories

Current Resilio still leaves later operators to reconstruct whether the honest sentence is:

- `app is locked, but OS Recents exposure is reduced`
- `external edit is copy-return, not live provider editing`
- `forgetting the local secret only blocks local access`
- `forgetting the local secret requires reinstall and local-only data loss`

That sentence should belong to one page and one receipt, not a settings page plus peculiarities plus an editing tutorial.

## The tighter AnonSync conclusion

AnonSync should borrow the following from Resilio more boldly:

- candid admission that mobile app protection affects system integration
- candid admission that outside-app edit flows are often copy-return rather than live edit
- candid admission that local-only mobile data can have a different recovery ceiling from replicated data

But AnonSync should refuse the exact page contract whenever one ordinary answer still depends on:

- a settings article
- an iOS peculiarities article
- a separate iOS edit tutorial
- a storage-management page
- a Windows Phone limitations page

## The replacement pages this evaluation justifies

This pass therefore makes four page-shaped obligations concrete:

1. **Local protection** — what exactly is protected, what OS surfaces disappear, and what recovery cliff exists?
2. **Protection change review** — what visibility, edit-lane, or local-data consequences follow if protection changes here?
3. **External edit lane** — is this live provider editing, copy-return editing, branch creation, or blocked?
4. **Local protection receipt** — what changed in lock posture, OS visibility, edit lane, and recovery ceiling?

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that local mobile privacy controls and outside-app editing are real product contracts, but it is also current evidence that one ordinary question — `what exactly changes if I protect this app or open this file in another app?` — can still require settings prose, platform peculiarities, an edit how-to, and storage notes just to learn that OS Recents visibility changed, the edit lane is copy-return rather than live, and the local recovery ceiling may be lower than the operator assumes. AnonSync should copy the candor and refuse the scattered contract.
