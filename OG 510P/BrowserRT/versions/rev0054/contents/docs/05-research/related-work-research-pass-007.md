# Related work research pass 007 — content-addressed storage, manifests, and fake providers

Revision: rev0028

## Why this pass exists

BrowserRT now has browser OPFS async and worker sync-handle proofs, but it still lacks the storage nucleus that can absorb those APIs without becoming ad hoc file I/O. This pass steals from systems that treat storage as named objects, logs, manifests, caches, and testable providers.

## Stolen ideas

### Git object storage

Git's object model reinforces a key BrowserRT rule: bytes can become stable object identities. The immediate steal is not Git's full history model; it is the habit of naming immutable payloads by digest and then building higher-level references on top.

BrowserRT implication: a `block` ref should include provider, digest algorithm, digest, byte length, and label. It should be cheap to prove that identical bytes create the same identity.

### Bazel remote cache and CAS

Bazel remote cache separates action metadata from content-addressed output files. The useful idea is not remote caching itself; BrowserRT is cloudtainer-only and local-first. The useful idea is: reproducible actions can be keyed, and byte outputs can live in a CAS independent of the action that produced them.

BrowserRT implication: future test caching, replay artifacts, and storage blocks should share object-ref vocabulary.

### SQLite / PostgreSQL / RocksDB WAL pressure

WAL systems teach the same boring lesson: durable state changes need a log before they are considered committed. RocksDB's WAL and MANIFEST split is especially useful: one log recovers in-memory writes, while the manifest records storage-state edits.

BrowserRT implication: rev0025 does not implement a WAL, but the fake block store should create the test vocabulary for future journal, manifest, compaction, and recovery slices.

### RocksDB MANIFEST

The MANIFEST pattern is a warning against trusting file discovery after crashes. BrowserRT should eventually have a transactional manifest of storage-state changes rather than trying to infer truth by listing OPFS files.

BrowserRT implication: future OPFS block storage should test manifest recovery separately from basic write/read.

### S3 object consistency

Object stores make consistency promises explicit. BrowserRT cannot make S3-like guarantees in a browser origin, but it can name weaker guarantees: read-after-write inside one provider instance, verified block checksums, and no multi-tab durability claim until tested.

BrowserRT implication: every provider must publish consistency claims and every claim needs a manifest task.

### Model-based and fake-provider testing

Model-based testing vocabulary says to run commands against both a simple model and the real system. BrowserRT should use this early, with deterministic seeds, before expensive browser/storage/mesh tests.

BrowserRT implication: rev0025 adds a fake provider proof with deterministic command history, checksum verification, fault injection, and corruption detection.

## Ambitious dream

BrowserRT storage could become a local object substrate:

```txt
object refs -> block refs -> provider -> journal -> manifest -> compactor -> replay
```

Providers could include:

- memory fake provider;
- Node filesystem provider for cloudtainer tests;
- OPFS async provider;
- OPFS sync-worker provider;
- OPFS access-handle pool provider;
- quota-pressure fake provider;
- crash/reorder/partial-write fake provider;
- future mesh-coordinated provider with Web Locks.

The dream is not "a database". The dream is the storage substrate that lets later databases, media caches, vector indexes, traces, and local app state share one runtime contract.

## Tempering rule

No storage dream gets promoted unless it has:

```txt
provider contract + object ref + trace events + fake-provider test + browser-provider test + non-claim boundary
```

Rev0011 adds only the fake-provider test and content-addressed block-store skeleton.
