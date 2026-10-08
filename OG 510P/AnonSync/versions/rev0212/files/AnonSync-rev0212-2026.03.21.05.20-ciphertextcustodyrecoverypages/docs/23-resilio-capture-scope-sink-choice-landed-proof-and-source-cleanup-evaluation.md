# Resilio capture scope, sink choice, landed proof, and source cleanup evaluation

## Purpose

The archive already has stronger answers for subject-kind choice, constrained-seat storage, capture-only ingest, external editing, background freshness, and mobile storage.
What still remained under-specified was another ordinary but load-bearing non-clone seam:

> current Resilio docs are fairly candid that mobile capture and backup are special workflows with different retention and runtime behavior, but the operator still has to reconstruct one coherent answer from Camera Backup, Android backup, Simple Mode, QR intake, and mobile storage/runtime articles.

This document tightens that line.
It does not argue that Resilio lacks useful ingest workflows.
It argues that the capture truth is still spread across too many surfaces to earn direct interface cloning.

## Bottom line

Resilio still deserves credit here.
Current official docs still show all of the following are real and useful:

- camera backup and Android backup are treated as distinct workflows, not merely renamed generic sync folders
- current docs are candid that Android can back up virtually any reachable data while iOS can only back up Camera Roll because apps cannot read outside their own folder
- current docs are candid that deleting backed-up files on the source can leave copies intact on the sink and that disconnecting backup does not retroactively delete already-landed pictures
- linked-device selection, mobile placeholders, and constrained storage classes are all exposed as practical operator concepts rather than hidden implementation accidents

Those are good instincts.
But the same docs also show why AnonSync should not clone the page contracts.

## The four load-bearing non-clone seams in this pass

### 1) Capture source scope is useful, but still article-shaped

Current official docs still say all of the following at once:

- Camera Backup uses a camera-domain workflow whose default desktop-side folder names differ by platform
- Android backup can target virtually any kind of reachable data, including custom folders
- iOS can only back up Camera Roll because app sandbox rules block access to other locations
- Android Simple Mode changes what source and path choices are visible during adjacent intake workflows

That is useful power.
It is still not one ordinary page answering:

> what exact source domain is attached here, what permission proves it, and what runtime/platform caveat narrows it?

### 2) Sink choice is real, but still split across link delivery, linked-device pickers, and storage caveats

Current official docs still say all of the following at once:

- Camera Backup shows linked devices and lets the user select them by checkbox
- Android backup can immediately target one of the linked devices, or else emits a link for delivery to another device
- default backup folders are created on the chosen desktop/storage target with legacy read-only backup semantics
- Android path and SD-card behavior still depend on Simple Mode, provider grants, and existing-folder-only caveats in some flows

That is respectable practicality.
It is still not one ordinary page answering:

> which sinks are in this ingest relationship right now, what storage/path rules constrain each sink, and which of those choices were operator-chosen versus platform-forced?

### 3) Landed-copy truth is still weaker than it should be

Current official docs still say all of the following at once:

- backup detail surfaces show number and total size of files to be backed up
- backup can pause/resume and list chosen devices
- Android backup emphasizes retention after source-side deletion once files have been backed up
- background/runtime limitations differ by platform, especially for iOS and Android

That means the product hints at progress and durability.
It still does not publish one exact answer to:

> has this item only been discovered, has it actually landed on a durable sink, or is the user merely seeing an optimistic queue/progress surface?

### 4) Source cleanup truth is candid, but still support-shaped

Current official docs still say all of the following at once:

- deleting backed-up files from Android leaves copies intact on the computer sink
- desktop has read-only access in Android backup workflows, so sink-side deletions do not flow back to the phone
- disconnecting Camera Backup leaves the already-present pictures on both devices intact
- iOS and some older mobile families require the app to stay open for real-time backup

That is good retention candor.
It is still not one ordinary page answering:

> if I delete from the source, pause, or disconnect, what exactly survives, what promise was already earned, and what future ingest stops?

## What AnonSync should copy

AnonSync should copy the useful parts more boldly:

- explicit capture-only ingest as a first-class workflow
- source-domain candor rather than pretending every seat can watch every path
- real sink choice rather than fake `backup to cloud` abstraction
- retention floors that protect already-landed bytes from source-side cleanup
- explicit runtime/background caveats for mobile capture sources

## What AnonSync should refuse to clone

AnonSync should refuse the exact current page contracts where:

- source scope depends on reading separate camera, Android backup, and platform limitation articles together
- sink assignment depends on mentally merging linked-device selection, link delivery, Simple Mode, and storage-grant caveats
- landed-proof truth depends on generic progress counters rather than a durable threshold page
- source cleanup truth depends on remembering several articles about delete/disconnect/runtime behavior

## The replacement pages this revision adds

This revision therefore adds four ordinary replacement pages:

1. **Capture source** — what exact source domain is attached, what permission proves it, and what runtime caveat currently matters
2. **Capture sink chooser** — which sinks participate, under what storage/path constraints, and by what admission route
3. **Ingest landed proof** — whether a source item is merely seen, in flight, or durably landed under policy
4. **Source cleanup review** — what source-side delete, pause, and disconnect would preserve or stop right now

## Result

The Resilio stance is now tighter again:

> borrow the capture and backup convenience; refuse the article-scattered page contracts; replace each refusal with one ordinary page that makes the operator answer local, exact, and reviewable.
