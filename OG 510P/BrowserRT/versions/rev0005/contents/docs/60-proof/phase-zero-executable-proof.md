# Phase-zero executable proof

rev0005 converts the rev0002 ambition into one narrow executable slice. The proof
is intentionally tiny: it is not a scheduler, not a browser conformance harness,
and not a performance benchmark. It is the first end-to-end kernel behavior that
must stay green before BrowserRT grows broader.

## Proven surfaces

1. **boot report**: `createBootReport()` and `rt.report` expose revision,
   version, detected capability posture, available tiers, lanes, priorities, and
   the current executable-proof flags.
2. **trace log**: `TraceLog` records ordered events with sequence numbers.
   Runtime boot, report, channel activity, object transfer creation, worker
   calls, worker exit, supervisor restart, and close are visible.
3. **bounded channel**: `BoundedChannel` exercises explicit overflow behavior;
   the proof uses `drop-oldest` and verifies that the retained value is the
   newer one.
4. **worker agent**: `WorkerAgent` spawns a Node worker-thread backend inside
   the cloudtainer and calls a tiny method protocol.
5. **transferable object ref**: `createTransferObject()` binds an object ref to
   an `ArrayBuffer` transfer list. The proof verifies caller-side detachment and
   worker-side summing of transferred `Uint32Array` contents.
6. **supervisor restart**: `Supervisor` observes an intentionally crashed
   worker, spends one restart budget, creates a new agent, and successfully
   routes a post-crash call.

## Canonical commands

```bash
make test
make proof
make lint
```

`make proof` rewrites `artifacts/proof/REV0005-PROOF-RUN.json`. `make test` and
`make lint` run the proof without rewriting the artifact.

## Canonical witness

The machine-readable witness is:

```txt
artifacts/proof/REV0005-PROOF-RUN.json
```

It records checked claims, normalized trace events, required event kinds, and
observations for channel overflow, buffer detachment, transfer sum, crash
rejection, and restart recovery.

## Explicit non-claims

- This is a Node worker-thread proof, not yet a browser Worker/CDP proof.
- There is no OPFS lane yet.
- There is no SharedArrayBuffer ring yet.
- There is no WebGPU lane yet.
- There is no cross-tab mesh yet.
- There is no real-device performance claim.

## Why this proof matters

The proof touches the primitive families BrowserRT must not fake later: boot
posture, trace evidence, bounded queues, agent lifecycle, data-plane transfer,
and supervision. Future ambition should attach to these primitives instead of
replacing them with ad hoc demos.


## Rev0005 addition

Rev0005 adds `test/surface-inventory.json`, `test/impact-map.json`, `test/quarantine.json`, affected-file planning via `--changed`, `tools/plan_tests.mjs`, `tools/validate_test_surface.mjs`, and `tools/run_tests.mjs timing summaries`. Future expensive browser/storage/GPU tests should enter as small manifest slices with timing evidence and non-claims.
