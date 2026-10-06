# Test pyramid and slices

Revision: rev0005.

BrowserRT's test pyramid is not only about unit versus integration tests. It is
about turn economics.

## Pyramid

1. **Contract checks**: docs, receipts, JSON, manifests, no dependency drift.
2. **Pure Node unit checks**: hashes, envelopes, selection, impact maps.
3. **Node worker checks**: worker spawn, transfer, crash, supervisor restart.
4. **Browser capability checks**: browser boot, Worker, SAB, OPFS, WebGPU,
   OffscreenCanvas, WebCodecs, BroadcastChannel, Web Locks.
5. **Lane integration checks**: CPU/storage/GPU/render/media/mesh interactions.
6. **Chaos checks**: kill, quota, corruption, cancellation, replay.
7. **Demos and benchmarks**: useful for regressions, not a substitute for the
   lower layers.

## Slice law

A future expensive proof must enter as a tiny capability probe first. For
example, OPFS should not arrive as a full storage engine test. It should arrive
as:

- async OPFS smoke;
- sync worker access handle smoke;
- cleanup/isolation proof;
- block-store write/read proof;
- crash-recovery proof.

Each gets a manifest id, timing estimate, timeout, isolation mode, and artifact
policy.

## Release tier today

The current release tier is intentionally small:

- harness selftest;
- surface inventory validation;
- runtime smoke;
- phase-zero agent/supervisor proof.

The audit tier runs cube checks. The full tier includes everything currently
available.
