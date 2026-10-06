# Validation slice — scheduler:cross-lane-contract-proof

Revision: rev0031

This slice proves the fake-provider cross-lane scheduler contract.

## Manifest task

```txt
scheduler:cross-lane-contract-proof
```

Command:

```txt
node tools/cross_lane_scheduler_probe.mjs --json artifacts/validation/REV0044-CROSS-LANE-SCHEDULER-PROBE.json
```

## What it proves

The proof checks dependency deferral, lane capacity, fallback routing, no-mutation rejection, and trace evidence.

The proof checks:

- critical interactive work dispatches before lower-ranked lane work;
- lane capacity is enforced and emits `crosslane:lane-at-capacity`;
- another lane can make progress while one lane is full;
- dependency deferral: a task with `dependsOn` waits until its parent completes, with `crosslane:defer-dependency` evidence;
- an unhealthy lane rejects work without fallback;
- an unhealthy lane can route through a declared healthy fallback lane;
- a healed lane can accept direct work again;
- oversize, duplicate, and unknown-lane rejections do not mutate queued/running state;
- all accepted tasks complete and the final queue/in-flight set is empty;
- required trace event vocabulary is present.

## Artifact

```txt
artifacts/validation/REV0044-CROSS-LANE-SCHEDULER-PROBE.json
```

The artifact includes observations, final scheduler snapshot, trace kinds, dispatch order, and explicit non-claims.

## Audit task

```txt
facility:scheduler-contract-audit
```

The audit regenerates the proof if needed and then checks source/docs/manifest/proof/non-claim coherence.

## Non-claims

- No production scheduler claim.
- No browser Worker scheduler proof.
- No real preemption or OS-thread scheduling claim.
- No work-stealing implementation claim.
- No latency, throughput, or fairness-SLO claim.
- No OPFS, WebGPU, render, media, or cross-tab provider integration proof.
