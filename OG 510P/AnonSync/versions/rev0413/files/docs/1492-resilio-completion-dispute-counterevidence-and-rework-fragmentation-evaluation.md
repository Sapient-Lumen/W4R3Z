# Resilio completion-dispute, counterevidence, and rework fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- issue a mandate
- receive a fulfillment attestation
- accept, partially accept, or leave residual duty visible

What it still lacked was the next ordinary operator answer:

> when the delegate says the work is done, some witnesses look green, and the requester or downstream state still disagrees, which witness wins, what burden applies, and do we uphold, narrow, overturn, or send the work back for rework?

That is the seam this pass locks.
Accepted completion is not the end of the story if the claim is later challenged.
Observed health is not the same thing as uncontested fulfillment.
A challenged return needs a durable adjudication object, not a new chat thread.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real witness planes that can disagree with each other in ways that matter to an operator:

- `Sync Main View (Desktop)` still says green check means files are synced with all connected peers, History shows the last 30 days of general syncing activity, and peer counts distinguish online peers from total peers.
- `Comprehensive guide to syncing (Desktop-Desktop)` still says a remote device can remain in `Pending approval`, and that if the source side receives no approval request the condition indicates a network-connectivity problem between the devices.
- `User Management` still says permissions can be changed without disrupting synchronization and that disconnect revokes future updates while already synchronized files remain in place.
- `"Time difference" error` still says Sync decides which file is newer by comparing modification time after converting to GMT, and that a bad time or timezone can produce warnings and even an empty file list on mobile.
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` still says one peer can announce new or updated files while later there are no source peers holding those files to actually provide them.
- `Conflict files in Sync` still says multiple versions may try to land into a single file or folder and produce conflict files for several filesystem-related reasons.
- `Disconnecting and Removing Folders` still says disconnect removes placeholder files if Selective Sync was enabled, and reconnect can later propose a different path and possibly create a new directory.
- `My files don't sync` still says the operator may need to inspect peers, warnings, History, selective-sync status, or even re-add the folder, which reinforces that different witness planes can point in different directions.

## What current Resilio still gets right

### 1) It exposes several real witness families

UI state, approval state, peer state, history, warnings, file-level conflict artifacts, and troubleshooting guidance are all real.
That is worth borrowing.

### 2) It is candid that `looks connected` can still hide a real blocker

Green checks are scoped to connected peers.
Pending approval may really be a connectivity problem.
Bad clocks can make ordering wrong.
Source peers can disappear after announcing updates.
That honesty is useful.

### 3) It preserves some irreversible consequences that matter to adjudication

Disconnect can leave old bytes in place while suspending future updates.
Selective-sync placeholder removal changes local evidence.
Conflict files and path forks can create visible aftermath that must be explained.
That is good raw material.

## Where current Resilio still fragments the operator answer

### A) There is no canonical completion-dispute object

Resilio gives the operator green state, history rows, warnings, troubleshooting pages, and conflict artifacts.
What it still does not give is one first-class object answering:

- what exact completion claim is being challenged
- who is challenging it and on what basis
- what counterevidence has been attached
- which witness family has priority for this claim type
- what burden of proof is still unmet
- whether the right verdict is uphold, narrow, overturn, rework, or reopen

### B) Visible activity and accepted fulfillment can diverge

A share may look healthy with connected peers while the wrong peers are absent.
A requester may see `Pending approval` while the source sees no request because the path is blocked by connectivity.
A mobile peer may show an empty list because of time skew while another witness plane looks calmer.
A disconnect can leave old bytes present, which makes `files are still there` weaker than `future updates are still authorized and flowing`.

### C) Counterevidence is scattered by symptom family

Conflict files, time skew, no-source-peer conditions, placeholder removal, and peer disconnect each live in separate documentation lanes.
That forces the operator to reconstruct one dispute answer from several articles and UI fragments.

### D) Rework truth is left to operator folklore

When a completion claim is narrowed or overturned, current Resilio offers raw troubleshooting and manual next steps.
It does not provide one durable adjudication object that says exactly what portion was disproved, what burden remains, and what rework is now required.

## Hard product decision unlocked by this pass

AnonSync should not let a challenged completion claim dissolve into another chat note or a generic `still syncing` badge.
It should promote any material disagreement into a first-class **completion dispute** that separately expresses:

- challenged fulfillment claim
- challenger and challenge basis
- witness families and witness priority
- burden still unmet
- adjudication verdict
- required rework or surviving acceptance scope
- appeal / reopen boundary

## Replacement line for AnonSync

Borrow from Resilio:

- visible green-state, history, warning, conflict, peer-state, and approval witnesses
- candor that those witness planes can disagree for legitimate reasons
- honesty that connectivity, time skew, placeholder posture, and source availability can all change what a witness means

Do not clone from Resilio:

- any workflow where a green check or history row silently wins a completion dispute
- any contract where conflicting witnesses are only reconciled through operator memory and troubleshooting folklore
- any product shape where partial overturn, narrowed acceptance, or required rework are not durable first-class verdicts
- any interface where the challenger cannot see what burden remains unmet before stronger completion language becomes allowed again

AnonSync should instead ship explicit pages for:

- completion dispute contract sheet
- counterevidence adjudication review
- dispute verdict proof
- completion dispute timeline
- completion dispute lineage receipt
