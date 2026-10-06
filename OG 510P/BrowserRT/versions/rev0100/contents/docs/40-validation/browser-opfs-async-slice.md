# Browser OPFS async slice

Revision: rev0028

Task id: `browser:opfs-async-proof`

This slice proves one narrow thing: inside the managed Chromium/CDP fixture,
BrowserRT can use the browser's async OPFS APIs to write bytes, read them back,
create an OPFS object ref, emit storage trace events, and restore the fixture.

## Why this slice exists

OPFS will become BrowserRT's likely persistent storage provider. But storage can
turn into a giant monolith quickly. This slice deliberately avoids sync access
handles, block stores, journaling, quota pressure, crash recovery, and multi-tab
locking. It only proves the async browser file path and the trace/object-ref
surface.

## Proof shape

The command:

```bash
node tools/run_tests.mjs --tier browser --id browser:opfs-async-proof --jobs 1
```

The probe:

```txt
start local server with COOP/COEP headers
relax managed Chromium URL policy if needed
launch headless Chromium
attach CDP
import BrowserRT
boot runtime with browserOpfsAsyncProbe flag
call rt.opfsAsyncWriteReadProbe
write file through createWritable
read file through getFile / arrayBuffer
assert same byte count and digest
create OPFS object ref
record trace events
teardown browser/server/profile
restore policy
write artifact
```

## Required artifact evidence

The artifact must show:

- `status: passed`;
- current revision and version;
- `crossOriginIsolated: true` for the fixture page;
- OPFS availability via `navigator.storage.getDirectory`;
- `bytesWritten == bytesRead`;
- `same: true`;
- object ref kind `opfs`;
- provider/backend `opfs-async`;
- trace events for OPFS start/result and OPFS object ref;
- policy restoration flag;
- per-phase timings.

## Non-claims

- This is not a sync access handle proof.
- This is not a worker-storage proof.
- This is not a block store.
- This is not a durability or crash-recovery proof.
- This is not a quota or eviction proof.
- This is not a multi-tab concurrency proof.
- This is not a performance benchmark.
