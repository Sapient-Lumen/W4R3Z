# Synchronization attempt journal v1

The journal is operational restart state, not a synchronization root. It is one private mode-0600,
owner-owned, single-link file under the namespace root and is serialized by the same namespace
transaction as staging and object commit.

```text
signed journal
  namespace ID
  mutation + prior-record digest
  high attempt ID
  zero or more active attempts, sorted by ID

active attempt
  attempt ID
  immutable object kind + SHA-256 digest + exact bytes
  signed-inventory route public key
  worker incarnation
```

IDs are durably burned before `SyncObjectScheduler::assign`. An active record is added before the Tox
receive resume effect and removed only after staging has been committed or discarded. Active count is
bounded by both the store configuration and the namespace outstanding-request quota.

Recovery holds the namespace transaction and applies this order:

1. load and verify the exact stable-device signature and namespace policy bounds;
2. verify an existing final object, or strictly commit the attempt's staging file;
3. classify valid final bytes as committed;
4. classify absent or safely removable corrupt staging as fenced;
5. retain and fail closed on uncertain I/O, unexpected shape, or corrupt final-store state;
6. clear all classified active entries in one signed atomic replacement.

No file number, path supplied by a peer, scheduler vector index, accepted HEAD, or activation pointer
appears in this record. Complete older signed-record replay is not claimed to be prevented without an
external monotonic witness.
