# Resilio finish forecast, remaining work, and ETA-confidence fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- prove that work was alive
- separate motion from net progress
- show churn and no-net-gain boundaries
- trigger reroute or rescue when busy work stopped buying real reduction of the obligation

What it still lacked was the next ordinary operator answer:

> given the current progress truth, what can we now honestly forecast about finishing, how much obligation remains, and how believable is any ETA or deadline claim?

That is the seam this pass locks.
A product that can say work is truly advancing but still cannot say whether it is finishable soon, later, or not honestly forecastable yet still leaves too much truth trapped in graph watching and ad hoc optimism.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **forecast ingredients**, but mostly as separate operational surfaces rather than one operator-facing forecast contract:

- `Performance overview` still exposes only short real-time windows — 1 minute, 10 minutes, and 1 hour — with per-peer speed, latency, and disk queue detail.
- `How soon does synchronization start?` still says change discovery may be immediate through filesystem notifications, or delayed until scheduled rescan every 600 seconds and on start, and that `folder_rescan_interval = 0` disables rescans even on restart.
- `Running Sync on schedule` still says paused hours stop ordinary upload/download but do not stop zero-sized-file sync, deletion propagation, and rescanning/indexing.
- `Power user preferences` still lists forecast-shaping settings such as `direct_torrent_enabled`, `prioritize_initial_indexing`, `parallel_indexing`, `recheck_locked_files_interval`, and `folder_rescan_interval`, each capable of changing how quickly visible work can actually finish.
- `Some internal tasks are taking time to complete` still says hidden work like checking blocks, deduplication copy, hashing, merging, scanning, reading, and writing can consume time without yet proving that final obligation is near completion.
- `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` still says only changed pieces are normally transferred, but if pieces shift then the whole file is re-synced unless a Business-only delta feature applies.
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` still shows that peers can be told work exists and only later discover that no source can actually provide the bytes.
- `Locked files` still shows that the work can remain pending because another application has blocked access entirely.

## What current Resilio still gets right

### 1) It exposes many of the variables that distort any naive ETA

Short-window speeds, disk load, queue depth, rescans, schedule pauses, and hidden preprocessing are all real forecast ingredients.
That candor is worth borrowing.

### 2) It admits that discovery time and transfer time are different phases

The rescan article and scheduler article both make clear that bytes are not the whole story.
A system may still be detecting, indexing, or waiting for its next allowed transfer window.

### 3) It names several conditions that can collapse forecast confidence

Locked files, ghost-file conditions, and whole-file re-sync after shifted changes all teach the same lesson:
a visible trend line is still weaker than a reliable finish forecast.

## Where current Resilio still fragments the operator answer

### A) Performance windows are still observation tools, not a finish contract

Current graphs can show what happened over 1 minute, 10 minutes, or 1 hour.
They still do not compile one explicit answer to what remains, whether the obligation is finishable under current conditions, or how wide the honest ETA window should be.

### B) Delay sources still sit on different surfaces

Scheduler pauses, rescan cadence, initial indexing delay, locked-file recheck intervals, and hidden preprocessing each affect finish time.
But current product/docs still make the operator collect those sources mentally rather than receiving one normalized forecast object.

### C) Partial-transfer efficiency and restart-from-start risk still coexist without one truth surface

Resilio help usefully says changed pieces are usually transferred, yet also says shifted changes can force whole-file re-sync and `direct_torrent_enabled` can restart a small file from the beginning after interruption.
That means optimistic byte-based ETA can be honestly wrong unless risk is published.

### D) The product still does not own `no honest forecast yet`

Current docs give many reasons forecast confidence may be weak.
But they still do not render one first-class answer that says the work is real, progress exists, and yet no narrow ETA claim is currently justified.

## Resulting product decision

AnonSync should borrow Resilio's candor that forecast depends on speed, delay windows, rescans, schedule rules, preprocessing, and availability failures.
It should **not** clone the contract where the operator still has to infer finishability and ETA confidence from scattered metrics, warnings, and advanced settings.

AnonSync should instead expose:

- one first-class **completion forecast contract sheet**
- one **forecast-quality review**
- one **finish forecast proof** page
- one **forecast timeline**
- one durable **forecast lineage receipt**

## Hard decisions locked by this pass

- **net progress is weaker than finish forecast**
- **finishability, ETA window, deadline confidence, and no-honest-forecast stay separate**
- **hidden preprocessing, schedule pauses, discovery lag, and retry risk must count against forecast confidence**
- **the product may honestly say `no narrow ETA` even while work is real and advancing**
- **forecast receipts must preserve remaining-obligation basis, finishability grade, ETA window, risk basis, and blocked stronger sentence**
