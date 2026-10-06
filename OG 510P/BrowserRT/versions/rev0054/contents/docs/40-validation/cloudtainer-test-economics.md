# Cloudtainer test economics

Revision: rev0028.

BrowserRT is constrained by validation cost as much as implementation difficulty.
The future suite will include workers, memory ownership, cancellation,
SharedArrayBuffer, OPFS, WebGPU, render, media, cross-tab mesh, chaos, replay,
and packaging checks. If these become one giant integration command, most turns
will be spent waiting or recovering from a vague failure.

The cube therefore treats the testing facility as infrastructure.

## Invariants

### BRT-TEST-001: tests are sliceable

Every meaningful test must have a stable id and be runnable independently or as
part of a declared tier.

### BRT-TEST-002: tests are timed

Every harness run records per-test `durationMs`, total duration, selected ids,
slowest tasks, and estimate misses. Untimed tests are invisible debt.

### BRT-TEST-003: tests have bounded timeouts

No test may rely on an endless global timeout. A timeout much larger than normal
runtime requires an explicit size and reason.

### BRT-TEST-004: parallelism is explicit

A test declares its lane and parallel group. The runner must know what can run
together and what must be serialized.

### BRT-TEST-005: sharding is available before pain

The test facility supports `--shard i/n` while the suite is still small, before
browser, GPU, storage, and mesh tests become expensive.

### BRT-TEST-006: turn-start checks are cheap

A future turn should begin with a fast smoke tier that proves the cube is coherent
before deeper edits happen.

### BRT-TEST-007: background processes are not canonical

Watch servers, local browsers, and daemons may be used inside one scoped harness,
but correctness must not depend on them surviving across assistant turns.

### BRT-TEST-008: affected selection is conservative

Affected-test selection may reduce work, but it must over-select rather than
under-select. Safety beats cleverness.

### BRT-TEST-009: isolation is declared

Each test declares whether it runs in a shared process, fresh process, exclusive
process, browser context, browser process, or manual surface.

### BRT-TEST-010: flake policy is explicit

A flaky test is either normal, suspected, or quarantined. Quarantine records must
be temporary and tied to a manifest id.

### BRT-TEST-011: browser processes are leased within a command

When browser tests arrive, a command may start a local server and Chromium/CDP
session for its own slice. It must also stop them. Cross-turn survival is a
non-claim.

### BRT-TEST-012: evidence beats vibes

Expensive tests should leave machine-readable artifacts: timing reports, traces,
screenshots, capability reports, or replay witnesses.

## Cost classes

| Class | Future examples | Risk |
|---|---|---|
| contract | docs, JSON, manifests | cheap but must stay frequent |
| unit | envelopes, hashes, channels | cheap and parallel |
| worker | spawn, transfer, crash | process startup matters |
| browser | CDP, local server, page probes | setup dominates |
| storage | OPFS fixtures, cleanup | state leakage and quotas |
| GPU | WebGPU device/pipeline | virtual graphics variability |
| mesh | multi-tab coordination | orchestration cost |
| chaos | kill/restart/quota/corruption | slow but essential |

The cube should optimize for many small, named, shardable checks rather than one
hero integration test.

## Rev0005 additions

Rev0005 adds schema-2 manifest metadata, `test/impact-map.json`,
`test/surface-inventory.json`, `test/quarantine.json`, affected-file planning,
dry-run reports, timing history, slowest-test analysis, and a stronger turn-start
process policy.

### BRT-TEST-013: browser policy is part of the fixture

A browser test is not green merely because Chromium launched. The fixture must
prove local navigation, page evaluation, capability observation, and restoration
of any temporary managed-policy changes. Policy relaxation belongs to a scoped
test command, not to a cross-turn daemon or hidden global setup.

## Rev0006 additions

Rev0006 adds the first managed browser/CDP boot slice. It is deliberately small:
local HTTP server, temporary policy relaxation, Chromium launch, CDP connection,
BrowserRT import, capability report, timing artifact, and teardown. It is the
pattern for future OPFS/SAB/WebGPU browser proofs, which must enter as separate
manifest tasks rather than expansions of one browser blob.
