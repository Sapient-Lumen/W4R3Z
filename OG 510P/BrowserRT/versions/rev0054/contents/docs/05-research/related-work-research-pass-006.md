# Related-work research pass 006 — storage workers, deterministic I/O, and audit discipline

Revision: rev0028

## Research posture

This pass asks what BrowserRT should steal now that it has a browser Worker proof
and an async OPFS write/read proof. The answer is not “build a database.” The
answer is to make BrowserRT’s storage lane look like a small, capability-scoped
I/O runtime: named providers, explicit request/completion records, worker-owned
sync handles, traceable object refs, bounded queues, cleanup policy, and future
journal/recovery contracts.

The sources are recorded by title/domain family in the research registry rather
than raw URLs, to preserve the cloudtainer-only/no-external-dependency cube
contract. The conversation answer cites the live sources.

## Source families reviewed

### OPFS and sync access handle surfaces

- `Origin private file system`, developer.mozilla.org.
- `FileSystemFileHandle createSyncAccessHandle`, developer.mozilla.org.
- `The origin private file system`, web.dev.
- `SQLite Wasm persistent storage options`, sqlite.org.
- `SQLite Wasm in the browser backed by the Origin Private File System`, developer.chrome.com.

Stolen idea: OPFS sync access is not just “faster file API.” It is a worker-only,
exclusive, byte-addressable surface. BrowserRT should treat it like a storage
provider that must be opened, leased, flushed, closed, traced, and fenced from
main-thread assumptions.

### Storage policy, quota, and eviction

- `Storage quotas and eviction criteria`, developer.mozilla.org.
- `Storage Buckets`, developer.chrome.com.
- `Storage Buckets explainer`, WICG.
- `Web Locks API`, MDN / W3C.

Stolen idea: BrowserRT storage must never pretend that browser-local persistence
is immortal. Future block-store work needs quota estimates, bucket/provider
hints where available, spill policy, lock policy, and non-claims about eviction.

### Durable state and actor-like runtime systems

- `Cloudflare Durable Objects overview`, Cloudflare Developers.
- `Cloudflare Durable Objects SQLite-backed storage`, Cloudflare Developers.
- `Azure Durable Task orchestrator code constraints`, Microsoft Learn.
- `Orleans overview`, Microsoft Learn.
- `Dapr Actors overview`, Dapr docs.

Stolen idea: persistent local workers should eventually have identities,
activation/deactivation policy, deterministic orchestration boundaries, and
state ownership. BrowserRT should not clone Durable Objects in the browser, but
it can steal the nouns: object identity, private storage, alarms/reminders,
serial turns, and hibernation-like lifecycle.

### Deterministic testing and model-first failure discovery

- `FoundationDB Simulation and Testing`, FoundationDB docs.
- `FoundationDB Engineering`, FoundationDB docs.
- `Deterministic simulation testing`, Antithesis docs.
- `Use of Formal Methods at Amazon Web Services`, ACM/AWS paper family.

Stolen idea: for BrowserRT, complex storage/mesh behavior should eventually be
specified as small state machines and tested in fake-provider simulation before
being trusted in real browser fixtures. The cube now treats the OPFS sync Worker
slice as an availability/correctness proof, not the storage engine itself.

## Design pressure extracted

1. **Storage provider is a capability, not a file path.** A provider says what it
   can do: async write, sync worker access, shared lock, quota estimate,
   flush, recovery, transaction, or none.
2. **Sync handles need leases.** The future API should expose an exclusive lease
   shape rather than letting arbitrary code hold a handle forever.
3. **Every write needs a completion event.** Request/completion thinking from
   async runtimes and I/O queues belongs in BrowserRT traces.
4. **Durability must be stated.** `written`, `flushed`, `manifested`,
   `journaled`, and `recovered` are different claims.
5. **Storage tests must decompose.** OPFS async, sync handle availability,
   journal write, recovery, quota pressure, and multi-tab coordination are
   separate slices.
6. **Audit is a runtime feature for the cube.** The more ambitious the project
   becomes, the more it needs explicit artifact hygiene and currentness checks.

## What rev0025 steals directly

Rev0010 steals the worker-only sync access handle shape and turns it into a
manifest task: `browser:opfs-sync-worker-proof`. The task proves a dedicated
module Worker can receive a transferred payload, call `createSyncAccessHandle`,
write/read/flush/close synchronously, return equal bytes, and emit OPFS object-ref
trace evidence. It does not claim durability, block-store correctness, or
performance.

It also steals the “trust evidence, not vibes” discipline from deterministic
systems testing and adds an explicit cube audit artifact: `REV0035-CUBE-AUDIT`.
