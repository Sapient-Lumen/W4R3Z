# Resilio deadline commitment, renegotiation, and breach fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- prove that work was real and alive
- separate motion from net progress
- forecast remaining work, finishability, and ETA confidence
- say when no honest forecast existed yet

What it still lacked was the next ordinary operator answer:

> when does a believable finish forecast become a real commitment, what conditions make that commitment conditional rather than hard, and how should miss, renegotiation, and breach stay visibly different?

That is the seam this pass locks.
A product that can publish a forecast but still cannot say whether anyone has actually promised a finish, under what conditions, and what survives after slip or breach still leaves too much truth trapped in chat and managerial folklore.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **commitment ingredients**, but mostly as separate operational surfaces rather than one operator-facing commitment contract:

- `Performance overview` still exposes only short real-time windows — 1 minute, 10 minutes, and 1 hour — with per-peer speed, latency, and disk queue detail.
- `How soon does synchronization start?` still says change discovery can be immediate through filesystem notifications or delayed until scheduled rescan every 600 seconds and on start, and that `folder_rescan_interval = 0` disables rescans even on restart.
- `Running Sync on schedule` still says paused hours stop ordinary upload/download but do not stop zero-sized-file sync, deletion propagation, or rescanning/indexing.
- `Power user preferences` still exposes commitment-shaping settings such as `folder_rescan_interval`, `direct_torrent_enabled`, `prioritize_initial_indexing`, `parallel_indexing`, and `recheck_locked_files_interval`.
- `Some internal tasks are taking time to complete` still says hidden work like block checking, deduplication copy, hashing, merging, scanning, reading, writing, and transferring can consume time without yet proving final completion is near.
- `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` still says only changed pieces are normally transferred, but shifted changes can force a whole-file re-sync.
- `Locked files` still says another application can block file access entirely, making transfer impossible until the lock clears.

## What current Resilio still gets right

### 1) It exposes many of the factors that make a promise fragile

Short-window throughput, rescans, schedule windows, whole-file restart risk, and lock recheck intervals are real promise-shaping facts.
That candor is worth borrowing.

### 2) It admits that visible activity is not the same thing as guaranteed finish

The scheduler, rescan, and hidden-task articles all make clear that transfer bytes are only part of the route.
A system can be active and still be waiting on discovery, preparation, or external release.

### 3) It preserves several meaningful blockers that should void overconfident promises

Locked files, source absence, heavy preprocessing, and whole-file restart risk all teach the same lesson:
a narrow ETA is still weaker than a durable commitment.

## Where current Resilio still fragments the operator answer

### A) Forecast ingredients are present, but promise class is still missing

Current docs can help an operator estimate.
They still do not compile one explicit answer to whether the current estimate is only aspirational, conditional, target-grade, or hard enough to call a commitment.

### B) Conditions that should void or renegotiate a promise still live on separate surfaces

Rescans, pauses, hidden work, lock rechecks, and whole-file restart risk all matter.
But the current product/docs still make the operator collect those conditions mentally rather than receiving one normalized commitment object with explicit invalidators.

### C) Slip and breach still blur together outside a dedicated contract

Current docs give many reasons delivery may slow, widen, or stop.
They still do not render one first-class answer that says whether the current state is a soft slip inside an allowed window, a renegotiation trigger, a missed target, or a hard breach.

### D) The product still does not own the public sentence after confidence degrades

Current docs give the ingredients for doubt.
But they still do not give one operator-facing place that says which earlier commitment survived, which one was withdrawn, and what weaker sentence remains publishable now.

## Resulting product decision

AnonSync should borrow Resilio's candor that promises are distorted by speed windows, rescans, schedule rules, preprocessing, restart risk, and blockers.
It should **not** clone the contract where the operator still has to infer whether anyone has truly promised a finish, under what conditions, and what miss or breach means.

AnonSync should instead expose:

- one first-class **delivery commitment contract sheet**
- one **commitment-quality review**
- one **delivery commitment proof** page
- one **commitment timeline**
- one durable **commitment lineage receipt**

## Hard decisions locked by this pass

- **finish forecast is weaker than commitment**
- **aspiration, target, conditional commitment, and hard commitment stay separate**
- **commitments must publish invalidators and renegotiation triggers explicitly**
- **slip, miss, renegotiation, withdrawal, and breach stay separate**
- **commitment receipts must preserve promise class, published window, invalidators, surviving weaker sentence, and breach boundary**
