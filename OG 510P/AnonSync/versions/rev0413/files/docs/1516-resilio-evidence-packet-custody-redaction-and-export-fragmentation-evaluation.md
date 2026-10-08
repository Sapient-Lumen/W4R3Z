# Resilio evidence packet, custody, redaction, and export fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- compare fact patterns against doctrine
- choose the next best discriminator
- rank the next evidence ask by burden and discriminator value
- record what came back from a chosen capture

What it still lacked was the next ordinary operator answer:

> now that we captured something material, what exact packet are we sharing, what was transformed or redacted, which source world produced it, how trustworthy is the export path, and what audience is allowed to rely on this form?

That is the seam this pass locks.
A product that can gather evidence but cannot package it honestly still leaves too much truth in support folklore.
Evidence that moves between people and systems needs its own contract.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful packet ingredients, but mostly as separate support instructions:

- `Collecting debug logs automatically` still routes logs through `Contact support`, asks the operator to include peer role, timestamps, and affected shares/files, and says not to close the application or device until sending is done.
- `Collecting debug logs manually` still routes another export path through manual attachment or upload, requires enablement, restart, reproduction, and gives different retrieval paths for desktop, service, LocalService, Local System, Linux, config-defined storage, NAS, and Android.
- `Collect debug logs on mobiles` still adds a mobile-specific path through a hidden `.synclogs` directory after a special debug action.
- `Where to collect logs on NAS?` still says each NAS keeps its own local storage for `.sync` state and may require checking config if the obvious log path is wrong.
- `Collecting crash reports, mini-dumps and core dumps` still introduces heavier artifact classes with different storage roots, and the service principal still changes where dumps live.
- `Collecting core dump on NAS devices` still includes moving a dump into a public folder for later download, which is an explicit packet-transform and custody event.
- `Errors & Troubleshooting` still presents these support-facing evidence instructions as clustered articles rather than one packet-shaping workspace.
- Current debug-log and dump articles still say direct technical support is available only for Sync Business customers and not for Sync v3 users.
- The current `Resilio Sync change log` still shows packet-transport facts like HTTPS sending for debug data in the Contact Support dialog and a prior fix for inability to send feedback.

## What current Resilio still gets right

### 1) It is candid that artifact classes differ

Logs, crash reports, mini-dumps, and core dumps are not treated as the same thing.
That is worth borrowing.

### 2) It preserves platform and runtime specificity

Desktop, mobile, NAS, service, and config-mode storage roots differ.
That honesty matters because source world affects packet meaning.

### 3) It admits that transport is part of the workflow

Contact-support upload, manual attachment, hidden mobile folders, NAS public-folder movement, and size limits all make the export path visible.
That is useful.

## Where current Resilio still fragments the operator answer

### A) Packet form still lives across separate support articles

Current Resilio helps gather artifacts, but still leaves the operator to infer what packet form is minimally sufficient for which audience.
Raw logs, dump files, support-form uploads, and narrative descriptions are spread out rather than normalized.

### B) Redaction and transformation cost are not a first-class contract

A moved dump in a public folder, a log excerpt pasted into text, or a summarized description all weaken or transform the evidence differently.
Current Resilio implies this reality but still does not make the cost explicit in one packet object.

### C) Custody and source world are visible, but not unified

Service principal, config `storage_path`, NAS local storage, mobile hidden paths, and manual versus automatic export all change how much confidence we should have in packet provenance.
Current Resilio shows the ingredients, but still does not compile them into one custody statement.

### D) `Sent` still does too much work

A packet can be sent, yet not received, not opened, not validated, or not usable.
Current Resilio instructions acknowledge parts of this, but still do not make these stages separate product truths.

## Hard product decision unlocked by this pass

AnonSync should not let evidence sharing live in email habits, support macros, or remembered path lore.
It should compile every serious export into a first-class **evidence packet** object that separately expresses:

- source artifacts and source world
- packet form
- redaction or transformation class
- custody chain
- audience envelope
- export path and transport result
- validation state after receipt
- diagnostic power preserved and diagnostic power weakened
- supersession and recall boundary

## Replacement line for AnonSync

Borrow from Resilio:

- its candor that artifact classes differ
- its platform-specific honesty about storage paths, service worlds, and config-defined local storage
- its explicit export steps for feedback forms, manual collection, mobile hidden folders, and NAS dump movement

Do not clone from Resilio:

- any workflow where packet form must be reconstructed from several support pages manually
- any contract where redaction or transformation can happen without publishing what it weakens
- any interface where `logs sent` pretends receipt, validation, and usability are already proven
- any product shape where old packets can linger without an explicit supersession or recall story

AnonSync should instead ship explicit pages for:

- evidence packet contract sheet
- packet-shaping and minimum-sufficient-share review
- export proof
- packet timeline
- packet lineage receipt
