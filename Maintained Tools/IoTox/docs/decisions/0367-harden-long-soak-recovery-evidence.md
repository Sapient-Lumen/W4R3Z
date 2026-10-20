# ADR 0367: Harden long-soak recovery evidence

Status: accepted and implemented
Date: 2026-09-10

## Context

The first source-linked three-writer 24-hour soak attempt reached the long-loop phase, not just
startup. It converged identity, authority, friendship, reciprocal read/write sharing, capacity,
offline conflict, explicit conflict resolution, and shadow cycles. It then rejected at writable soak
cycle 73 because one node had not projected the newest soak state before the per-cycle timeout.

That rejection exposed two harness problems.

First, rejected evidence was still too thin for late-soak diagnosis. The receipt retained aggregate
capacity, store, pull, branch, conflict, and high-water counters, but did not retain the tiny
content-free projection shape that would say which nodes had the latest synthetic soak files.

Second, the verifier still treated every rejected three-writer proof as though rejection must have
happened during capacity population. That was wrong once the run could reject after capacity had
already converged.

A third issue was a science-quality bug: the scheduled soak restart cadence selected the same node
for the 24-cycle profile. A long soak must rotate restart pressure across all writers.

## Decision

The three-writer soak harness now records a content-free projection shape for rejected soaks:

- whether the synthetic `current` and `toggle` leaves exist on each node;
- each leaf's byte count; and
- each leaf's SHA-256 digest when present.

It does not record synchronized file contents, real paths, Tox keys, stable principals, phrases, or
authority material.

The verifier now accepts full capacity projection in rejected proofs unless the failure was
specifically the capacity-population wait. Late-soak rejection can therefore remain valid retained
evidence instead of being rejected by an early-stage assumption.

Scheduled long-soak daemon restarts now rotate across nodes `a`, `b`, and `c`, and receipts record
the restart target sequence. This makes a 24-hour run a three-node restart campaign rather than a
single-node punishment loop.

Finally, the writable soak now has its own bounded stalled-cycle recovery path. When
`--soak-stalled-restart-after` is nonzero, a slow cycle first records lagging node identities by
local role name, captures wait-channel names, restarts the lagging nodes, runs a repair pass, and
then still requires the cycle to converge within the ordinary hard timeout. The 24-hour Sandwurm
profile sets this threshold to 120 seconds. A genuinely stuck cycle still rejects.

## Consequences

The next 24-hour run is more useful whether it passes or fails. A pass will disclose how many
scheduled restarts and stalled-cycle recoveries were required. A failure will retain enough
content-free shape to distinguish "capacity never caught up" from "late soak projection lagged on
one node" without mounting the guest disk.

This is a harness and evidence improvement, not a protocol correctness claim. It does not prove
precious-data suitability, independent backup safety, dishonest-storage behavior, cross-machine
behavior, or production filesystem diversity.

It also does not hide recovery. If the soak needs emergency restart/repair, that fact is part of the
receipt and the trust decision.

## Evidence

`python3 -m py_compile tools/run-sync-three-writer.py tools/verify-sync-three-writer-sandwurm.py`
passes.

`python3 tools/verify-sync-three-writer-sandwurm.py --self-test` passes with a late-soak rejected
fixture whose capacity projection is already complete, with a separate capacity-time rejection check.

`python3 tools/inspect-sync-three-writer-soak.py --self-test` still passes.

The dirty-tree smoke shakedown
`.sandwurm/lab/three-writer-soak-smoke/run.E5c9ajEe` independently verifies. It completed 3 writable
soak cycles over 34.389 seconds, recorded scheduled restart target `["a"]`, recorded zero
stalled-cycle recoveries, and completed the recovery/storage-fault follow-ups. Because it was run
before this ADR was committed, its source revision is intentionally dirty and it is not graduation
evidence.

The rejected first 24-hour attempt is retained at
`.sandwurm/lab/three-writer-soak-24h/run.AiIfjcKX`. It reached 72 completed writable soak cycles,
three daemon restarts, six repair passes, and 36 delete cycles before rejecting while waiting for
cycle 73.
