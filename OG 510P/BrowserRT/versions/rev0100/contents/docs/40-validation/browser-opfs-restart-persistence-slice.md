# Browser OPFS restart-persistence slice

Historical revision: rev0065

## Slice

`browser:opfs-restart-persistence-proof`

This slice is the first browser-process restart boundary proof for the async OPFS block-store provider. It writes a content-addressed block through `navigator.storage.getDirectory()`, verifies the digest in the first Chromium launch, tears down that browser process, relaunches Chromium with the same temporary profile and same local origin, reads the same OPFS block back, verifies the digest and byte count, deletes the block, and cleans up the namespace.

The point is not to promote a durability claim. The point is to replace a risky assumption with concrete evidence about one clean restart boundary in the cloudtainer Chromium fixture.

## Evidence

- Tool: `tools/browser_opfs_restart_persistence_probe.mjs`
- Browser fixture refactor: `tools/browser_cdp_fixture.mjs` supports an externally managed server via `options.server` and caller-provided profile directory via `options.profileDir` / `keepProfile`.
- Manifest task: `browser:opfs-restart-persistence-proof`
- Expected artifact: `artifacts/validation/REV0060-BROWSER-OPFS-RESTART-PERSISTENCE-PROBE.json`

## Required observations

- Same temporary profile is reused across two managed Chromium launches inside one proof command.
- Same local origin is served for write and read launches.
- First launch records OPFS block `put`, immediate `get`, `verify`, storage estimate, and trace events.
- Second launch records `has`, restart readback `get`, digest verification, `delete`, cleanup, storage estimate, and trace events.
- `StorageManager.persisted()` / `StorageManager.persist()` observations are recorded as environment facts only.

## Non-claims

- No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.
- No cross-browser conformance claim.
- No persistent-storage permission claim.
- No throughput, latency, SLO, retention-period, or real performance claim.
- No exactly-once delivery claim.

## Core non-claims

No production runtime claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.
