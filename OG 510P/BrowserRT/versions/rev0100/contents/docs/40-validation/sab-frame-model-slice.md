# Validation slice: `ipc:sab-frame-model-proof`

Revision: rev0028

This slice adds deterministic stateful testing for the variable-frame SharedArrayBuffer ring. It is deliberately cheap and release-tier eligible.

## Command

```bash
node tools/sab_frame_model_probe.mjs --json artifacts/validation/REV0044-SAB-FRAME-MODEL-PROBE.json
```

## What it proves

The probe runs 24 seeded scenarios and thousands of generated operations against the real `SharedFrameRing` while comparing externally visible behavior to a FIFO reference model.

It checks:

- `SharedArrayBuffer` and `Atomics` are available in the Node/cloudtainer runtime.
- Accepted push appends exactly one model frame.
- Rejected push does not mutate model length or push/pop counters.
- Oversize frames are rejected.
- Full-ring rejection is observed.
- Pop returns the oldest accepted frame.
- Empty pop does not invent frames.
- Wrap sentinels and reserved gap bytes are observed.
- Close rejects later pushes but still drains pending frames.
- Final snapshots have zero pending bytes.
- Trace event kinds are present.

## Why it exists

The previous `ipc:sab-frame-ring-proof` proves a worker-thread producer/consumer path. This slice is a different kind of proof: it attacks the state space with many generated command sequences before the browser variable-frame proof is attempted.

## Non-claims

- No browser Worker variable-frame proof.
- No MPSC or MPMC mailbox proof.
- No exhaustive formal model checking.
- No concurrent interleaving exploration.
- No `Atomics.waitAsync` proof.
- No WebAssembly shared-memory integration proof.
- No throughput or latency claim.
