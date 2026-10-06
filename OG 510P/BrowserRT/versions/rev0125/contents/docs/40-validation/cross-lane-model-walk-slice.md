# Validation slice — scheduler:cross-lane-model-walk-proof

Revision: rev0036

Manifest id: `scheduler:cross-lane-model-walk-proof`.

## Purpose

This slice is a deterministic seeded model-walk proof for the fake-provider `CrossLaneScheduler`. It compares live scheduler behavior with an independent `SchedulerOracle` after every generated operation.

## Command

```bash
node tools/cross_lane_model_walk_probe.mjs --json artifacts/validation/REV0044-CROSS-LANE-MODEL-WALK-PROBE.json
```

## What the proof exercises

- generated enqueue commands;
- generated duplicate, unknown-lane, oversize, unhealthy-lane, and queue-cost rejection paths;
- rejection no-mutation checks;
- generated lane health transitions;
- fallback routing;
- generated dispatch attempts;
- generated completions;
- dependency deferral;
- lane-capacity waits;
- final drain and empty accounting;
- trace event presence.

## Current expected shape

The proof currently runs 18 deterministic scenarios and at least 3,240 generated/random steps, plus scripted setup operations. The artifact must show model agreement after every generated step, current revision metadata, required trace events, and explicit non-claims.

## Why it is release-tier

The slice is Node-only, fake-provider, deterministic, and browser-light. It gives broad-release refactor confidence without launching Chromium or touching OPFS/WebGPU.

## Non-claims

- No exhaustive formal verification claim.
- No exhaustive formal model checking claim.
- No true concurrent interleaving or multi-threaded contention proof.
- No production scheduler claim.
- No browser Worker scheduler proof.
- No work stealing, preemption, priority inheritance, deadline scheduling, or DRF implementation claim.
- No throughput, latency, fairness-SLO, or real performance claim.
