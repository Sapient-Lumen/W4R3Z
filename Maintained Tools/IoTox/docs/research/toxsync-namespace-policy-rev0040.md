# toxsync namespace policy load contract

Date: 2026-08-20

Status: historical foundation; daemon integration and treepack-v1 were subsequently implemented.

Current amendment: ADR 0139 adds `treepack-v1` to the canonical engine set. The deferred-work list
below records the boundary of this original slice, not the current repository state.

## Decision

IoTox synchronization namespaces are local policy objects. A namespace is not a remote filename, Tox
friend number, Ratox profile name, or toxsync historical daemon record. The first imported slice adds
an IoTox-owned canonical namespace record and an atomic in-memory registry, while leaving remote HEAD
acceptance and protocol framing unallocated.

The record type is `iotox-sync-namespace-v1`. It binds:

- lowercase namespace id;
- normalized absolute non-root local root path;
- engine: `range-v1`, `content-v2`, or `treepack-v1`;
- activation mode: `disabled` or `manual`;
- artifact, manifest, store, staging, object, retained-revision, peer, lane, and outstanding-request
  quotas;
- exact sorted writer principals;
- exact sorted subscriber principals.

Every writer/subscriber key is an IoTox stable signing public key. At least one writer is required.
Writer and subscriber order must be canonical and duplicate-free. The policy record never grants
authority by itself. The later authority-ledger v3 allocation and `sync_authorization` gate now require
an exact-head proof plus the independent operation capability before this membership can admit work.

## Loader Boundary

`load_namespace_store(root, expected_owner_uid)` loads exactly:

```text
ROOT/namespaces/<namespace-id>.namespace
```

The root and `namespaces` directories must be normalized absolute paths, owner-only, no-follow, and
owned by the expected user. Record files must be regular, owner-only, single-link files. Any
unexpected top-level entry, unexpected namespace entry, symlink, hard link, mismatched filename/id, bad
owner, bad permission bit, oversized record, truncated read, unknown field, or noncanonical re-encode
fails the complete load.

The loader returns a vector of policies. `NamespaceRegistry::replace` validates the complete proposed
set before swapping it into memory and increments the generation only after success. Invalid
replacement leaves the previous registry snapshot and resolutions unchanged.

## What This Enables

This gives S1 a small, testable policy root before any remote sync traffic exists:

- local namespace identity separate from peer numbering;
- explicit engine and activation selection;
- quota checks before filesystem work;
- principal binding using current IoTox key types;
- deterministic rejection of ambiguous local state;
- generation-coherent reads for later worker and control surfaces.

## Deferred Work

The follow-on local accepted-HEAD store now implements a canonical
`iotox-sync-accepted-head-v1` state record under `accepted-heads/<namespace>.accepted-head`. It accepts
genesis only with an empty parent, advances only when the candidate parent equals the current accepted
record digest, treats exact repeated records as duplicates, and rejects stale generations,
same-generation forks, wrong namespaces, unauthorized writers, engine mismatch, generation jumps,
quota violations, and parent mismatch before durable mutation. Accepted records are persisted with
IoTox atomic state replacement and reload with canonical decode.

This slice intentionally does not implement:

- namespace create/update/delete CLI;
- durable atomic writes of namespace policy records;
- artifact/content store persistence;
- activation/current symlink or directory switching;
- Agent/control/protocol wiring of the implemented authority-ledger v3 sync admission gate;
- sync protocol feature numbers or packet families;
- daemon runtime projection;
- toxcore file-transfer integration.

Those remain S1/S2 work and must preserve the rule that receiving bytes never grants activation
authority.
