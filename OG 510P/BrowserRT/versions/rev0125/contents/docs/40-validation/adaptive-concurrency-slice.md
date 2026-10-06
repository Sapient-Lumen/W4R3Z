# Validation slice — adaptive concurrency proof

Revision: rev0028
Manifest id: `scheduler:adaptive-concurrency-proof`

## Purpose

Prove a cheap deterministic feedback-control slice before BrowserRT attempts provider-latency adaptive limits, browser Workers, OPFS integration, or fairness.

## Command

```bash
node tools/adaptive_concurrency_probe.mjs --json artifacts/validation/REV0044-ADAPTIVE-CONCURRENCY-PROBE.json
```

## What it proves

The compact slogan is: low-latency window increases, high-delay window decreases, timeout window decreases harder.

- the controller starts with a bounded initial limit;
- low-priority work is rejected at the soft adaptive limit;
- rejection does not mutate in-flight count or leases;
- critical work can bypass the soft limit;
- a hard maximum still rejects oversized critical work;
- healthy latency windows increase the limit;
- high-delay windows decrease the limit;
- timeout windows back off;
- provider-unhealthy state rejects low-priority work;
- provider health can recover;
- an explicit probe can force the minimum limit;
- final state has no leaked leases;
- trace events cover create, admit, reject, release, window, increase, decrease, provider health, and probe.

## Why this is release-tier

The slice is Node-only, deterministic, fake-latency based, and browser-light. It tests policy semantics without spending a Chromium/CDP launch.

## What it does not prove

- real latency measurement;
- production auto-tuning;
- fairness across many producers;
- browser Worker behavior;
- OPFS, WebGPU, or cross-tab integration;
- throughput or latency performance;
- exact Netflix, Envoy, TCP, CoDel, or SRE policy implementation.
