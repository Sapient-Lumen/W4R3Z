# Resilio execution principal, permission grant, and host authority evaluation

## Purpose

The archive already has stronger answers for state roots, surface parity, storage roots, host cadence, issue handling, and path continuity.
What still remained under-specified was another ordinary but load-bearing non-clone seam:

> current Resilio docs are fairly candid that service mode, runtime user, storage root, and host permissions materially change what the product can do, but the operator still has to reconstruct one coherent answer from Windows service guides, Linux package notes, NAS instructions, macOS headless instructions, storage-folder docs, and generic troubleshooting pages.

This document tightens that line.
It does not argue that Resilio hides these facts.
It argues that the facts still do not live on a few stable operator pages.

## Bottom line

Resilio still deserves credit here.
Current official docs still show all of the following are real and useful:

- Windows service installation explicitly says the service can run as the current user or as `Local System` / `Local Service`
- Linux package guidance explicitly says the default service runs as `rslsync` with minimum privileges and that a current-user alternative exists
- Synology guidance explicitly tells the operator which internal user must get read/write access
- generic troubleshooting explicitly says syncing fails when the runtime user lacks read-write access to the files and directory
- storage-folder docs explicitly show that runtime principal and launch mode change where settings, identity, logs, and share databases live

Those are good instincts.
But the same docs also show why AnonSync should not clone the page contracts.

## The four load-bearing non-clone seams in this pass

### 1) Execution principal is real, but still article-shaped

Current official docs still say all of the following at once:

- Windows service install asks for a user account and later shows the service logged on as that user
- Windows troubleshooting also recommends switching to `Local System` to reach folders the current user cannot write
- Linux packages default to `rslsync`, while a current-user service path is a separate alternative
- headless macOS guidance suggests creating a dedicated `resiliosync` user

That is useful candor.
It is still not one ordinary page answering:

> what exact OS principal is touching these bytes right now, why was that principal chosen, and what stronger or weaker world would exist under a different principal?

### 2) Permission grant truth is practical, but still split across host-specific articles

Current official docs still say all of the following at once:

- Linux package guidance requires adding `rslsync` to the current user's group and ensuring group read-write permissions for the synced folder
- Synology guidance requires granting the internal `rslsync` user explicit read/write access on the shared folder
- macOS headless guidance warns that group rw permissions must continue to hold or Sync will stop syncing new files
- troubleshooting says the runtime user must have read-write access to both the files and the directory itself

That is respectable practicality.
It is still not one ordinary page answering:

> what exact grant currently makes this path writable, how strong is that proof, and which missing grant blocks progress now?

### 3) Principal changes silently change local world and continuity risk

Current official docs still say all of the following at once:

- switching a Windows service from current user to `Local System` yields a different storage folder and a new empty-looking share set that must be re-added and re-connected
- storage-folder docs show different roots for ordinary desktop, Windows service variants, Linux package user choices, and NAS packages
- Linux command-line docs say default `.sync` storage lands in the current directory if no storage path is given
- config mode and storage-path changes can therefore move identity, logs, settings, and share database custody together

That is honest enough to help an expert.
It is still not one ordinary page answering:

> if I switch runtime principal, service mode, or storage root, am I still in the same local world or am I crossing into a successor world with continuity work ahead?

### 4) Filesystem authority repair is still troubleshooting-shaped

Current official docs still say all of the following at once:

- Windows service troubleshooting recommends Local System for folders the current user cannot write
- Linux guidance recommends group bridging and rw permission changes
- Synology guidance recommends granting the internal service user access
- generic troubleshooting says missing write access at either file or directory level can stall sync entirely

That is useful repair candor.
It is still not one ordinary page answering:

> what exact grant is missing, what is the least-destructive repair rung, and what evidence will prove the path is writable again after the fix?

## What AnonSync should copy

AnonSync should copy the useful parts more boldly:

- explicit publication of runtime principal rather than pretending the app is the only actor that matters
- explicit path-grant proof rather than generic `permission denied` prose
- explicit continuity warnings when principal or storage-root changes create a new local world
- explicit least-destructive repair ladders for blocked paths

## What AnonSync should refuse to clone

AnonSync should refuse the exact current page contracts where:

- execution principal truth depends on reading Windows, Linux, NAS, and macOS host articles together
- permission truth depends on host-specific lore about users, groups, rw bits, and folder-level grants
- principal switching and storage-root switching can silently create a different world that only later looks `empty`
- blocked-path repair lives in troubleshooting steps instead of one product-owned page

## The replacement pages this revision adds

This revision therefore adds four ordinary replacement pages:

1. **Execution principal** — what OS principal is running this seat, why that principal won, and what disk authority it currently holds
2. **Filesystem grant** — what owner/group/ACL/provider grant makes a path writable and where the proof is weak or stale
3. **Principal switch review** — whether changing runtime user, service mode, or storage root stays in the same world or creates a successor world
4. **Blocked-path repair** — what exact grant is missing, which repair rung is safest, and what retest proves recovery

## Result

The Resilio stance is now tighter again:

> borrow the honesty about runtime user, storage roots, and host permissions; refuse the host-article-shaped page contracts; replace each refusal with one ordinary page that makes OS authority local, exact, and reviewable.
