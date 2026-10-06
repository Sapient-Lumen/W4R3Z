# Validation slice — admission-control watermark proof

Revision: rev0028
Manifest id: `ipc:admission-watermark-proof`

## Purpose

Prove the first cheap overload-governance semantics before BrowserRT spends browser, OPFS, or multi-producer budget on admission control.

## Command

```bash
node tools/admission_watermark_probe.mjs --json artifacts/validation/REV0044-ADMISSION-WATERMARK-PROBE.json
```

## What it proves

- background frames are admitted until the high watermark is reached;
- low-priority work is rejected while congested;
- rejection does not mutate in-flight byte counts or leases;
- critical work can bypass congestion while staying below the hard limit;
- hard-limit rejection occurs when projected bytes exceed the cap;
- provider-unhealthy state rejects low-priority work;
- provider health can recover;
- draining and releasing accepted work crosses the low watermark and recovers;
- accepted frames still preserve FIFO through the spill mailbox;
- memory and spill paths both occur;
- trace events cover create, admit, high watermark, reject, release, low watermark, provider health, mailbox enqueue/spill/ack.

## What it does not prove

- adaptive concurrency or latency sampling;
- fairness among many producers;
- browser Worker behavior;
- OPFS spill/admission behavior;
- cross-tab pressure sharing;
- throughput or latency;
- cross-browser behavior.

## Why this is release-tier

The slice is Node-only, deterministic, and cheap. It protects overload semantics without launching Chromium.
