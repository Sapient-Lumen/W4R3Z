# Cloudtainer testability and shelf ledger

Current revision: rev0054

The cube must distinguish what can be built and tested in this cloudtainer from what requires external browsers, real hardware, real networks, or long-lived sessions.

## Rule

Do not delete a dream because it is hard to test. Put it on the right shelf.

Do not promote a shelved dream into a claim without repeated evidence.

## Evidence classes

### 1. Cloudtainer-buildable

These should be built and tested here first:

- fake-provider algorithms;
- deterministic model oracles;
- admission/retry/budget/resilience policies;
- object-ref and envelope contracts;
- Node worker-thread proofs;
- release-tier audit tools;
- docs and non-claim coherence checks;
- local server + CDP fixture code.

### 2. Smoke-testable in cloudtainer

These can receive narrow proofs here, but not broad claims:

- browser Worker spawn;
- SharedArrayBuffer rings when cross-origin isolation is configured;
- OPFS async behavior;
- OPFS sync access handles inside dedicated workers;
- page-reload readback in one temporary Chromium profile;
- local multi-tab Web Locks/BroadcastChannel experiments;
- simple WebGPU capability or compute smoke if available in Chromium/SwiftShader.

### 3. Needs external evidence

These should be developed behind fake providers or narrow probes, but their important claims require external evidence:

- real GPU/WebGPU throughput, latency, driver behavior, and thermals;
- WebNN/NPU behavior;
- mobile browser lifecycle and background behavior;
- real WebTransport HTTP/3 behavior;
- WebRTC WAN/NAT/TURN behavior;
- cross-browser conformance;
- browser storage quota/eviction behavior across devices;
- installability/native-app parity;
- long-session reliability.

### 4. Shelf until repeated container evidence

These are not abandoned. They require repeated proof attempts before promotion:

- WebTransport provider semantics inside this cloudtainer;
- multi-tab mesh stress beyond tiny CDP scenarios;
- browser crash/restart recovery semantics;
- OPFS quota pressure and eviction simulation;
- ServiceWorker/SharedWorker orchestration under reload/background conditions;
- WebGPU/WebNN provider calibration beyond smoke.

## Unshelf policy

A shelved capability may move back into active build work only after:

- three successful cloudtainer sessions across different revisions, or
- explicit external-device evidence with at least two distinct device/browser classes.

Every unshelf attempt must include:

- manifest task;
- trace artifact;
- failure-mode notes;
- source registry update;
- non-claim update.

## Hard current non-claims

- No WebGPU performance claim.
- No WebNN/NPU claim.
- No real WebTransport or WebRTC WAN/NAT claim.
- No mobile/background-lifecycle claim.
- No production security sandbox claim.
- No cross-browser conformance claim.
- No OPFS durability, fsync, quota, eviction, crash-recovery, or browser-restart claim.
- No exactly-once delivery claim.
- No production overload-governance claim.

## Why this matters

Future sessions will see less context than this revision can. This ledger exists to prevent them from either overclaiming or prematurely discarding good dreams.

Audit surface: `facility:mile-high-boundary-audit` keeps this cloudtainer shelf boundary legible.

Additional exact rev0044 non-claims:

- No new runtime provider behavior proof in rev0044.
- No OPFS durability, fsync, quota, eviction, crash-recovery, or browser restart claim.

Unshelf guard: do not promote a shelf item without the evidence above.
Unshelf exact phrase: three successful sessions are required before promotion unless external-device evidence exists.
