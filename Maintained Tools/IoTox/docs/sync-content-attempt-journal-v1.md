# Content-v2 attempt journal v1

Status: frozen; live multi-lane restart qualified on native carriers by ADR 0267, 2026-08-31.

## Purpose

`CTA1` is the stable-device-signed restart truth for active content-v2 receives. It exists separately
from `ATM1`: range-v1 attempts bind one bundle or range plan, while a content-v2 coordinator may have
many independently scheduled manifest pages and artifact chunks from several authenticated sources.

The journal is written before a file request or receive effect. A record binds the frozen signed HEAD,
logical object identity, exact object digest and size, exact Tox `FileId`, scheduler request/source IDs,
authenticated carrier incarnation, and stable source principal. None of those fields may be inferred
from a filename after restart.

The canonical path is:

```text
ROOT/content-attempts/NAMESPACE.active-content-attempts
```

`ROOT` and `content-attempts` are exact mode-0700 owner-owned directories. The journal is one
mode-0600 owner-owned single-link regular file read with `O_NOFOLLOW`; its descriptor metadata must
remain stable for the complete read. Atomic replacement uses the ordinary IoTox state-store primitive.

## Canonical encoding

All integers are unsigned big-endian. Reserved bytes are zero. The file is a 192-byte header, zero or
more 288-byte active records sorted by strictly increasing attempt ID, and one 64-byte detached
Ed25519 signature.

Header:

| Offset | Bytes | Meaning |
|---:|---:|---|
| 0 | 8 | magic `IOTXCTA1` |
| 8 | 1 | namespace length, `1..64` |
| 9 | 7 | zero |
| 16 | 8 | mutation, nonzero |
| 24 | 8 | high attempt ID, nonzero |
| 32 | 8 | active record count |
| 40 | 32 | stable device signing public key |
| 72 | 32 | prior complete-journal digest, or zero only at mutation 1 |
| 104 | 64 | namespace bytes and zero padding |
| 168 | 24 | zero |

Each active record:

| Offset | Bytes | Meaning |
|---:|---:|---|
| 0 | 8 | burned attempt ID |
| 8 | 1 | kind: `1` manifest page, `2` artifact chunk |
| 9 | 1 | carrier class: `1` primary, `2` auxiliary |
| 10 | 6 | zero |
| 16 | 8 | coordinator request ID |
| 24 | 8 | coordinator source ID |
| 32 | 8 | logical page/chunk index |
| 40 | 8 | exact object bytes |
| 48 | 8 | route-worker ID |
| 56 | 8 | route online epoch |
| 64 | 8 | remote route generation, zero for primary |
| 72 | 8 | primary-authority online epoch, zero for primary |
| 80 | 4 | tox friend number in that worker incarnation |
| 84 | 12 | zero |
| 96 | 32 | digest of the frozen canonical signed-HEAD record |
| 128 | 32 | exact page/chunk SHA-256 |
| 160 | 32 | exact Tox `FileId` |
| 192 | 32 | carrier route key |
| 224 | 32 | remote coordinator route key, zero for primary |
| 256 | 32 | stable source principal |

Active records may not share a request ID, FileId, or `(HEAD, kind, logical index)`. The active count
must fit both the local journal bound and the namespace outstanding-request quota. Each object size
must fit its kind, staging, and store quotas. A primary record has worker ID equal to online epoch and
no auxiliary fields; an auxiliary record requires every auxiliary incarnation field.

The signature covers SHA-256 domain `iotox-sync-content-attempt-signature-v1` over the exact header
and active records. `previous` is SHA-256 domain `iotox-sync-content-attempt-record-v1` over the prior
complete signed file. This detects mutation substitution relative to the current record but is not an
independent monotonic witness: a same-owner replay of an old complete journal remains outside the
claim.

## Mutation and recovery

Attempt IDs are burned by a signed mutation before scheduler assignment. `begin` then records the
complete binding before transport effect. Exact retry is idempotent; same-ID conflict and any active
request/FileId/logical alias fail closed. `finish` removes only an exact matching record.

The staging path is derived, never stored:

```text
ROOT/staging/content-v2/objects/HH/REST.REQUEST_ID.part
```

where `HH + REST` is the lowercase object digest. Startup does not resurrect a Tox transfer or trust
old friend numbers. During a live receive c-toxcore first writes through the file-transfer manager's
private pre-rename temporary:

```text
ROOT/staging/content-v2/objects/HH/.iotox-REST.REQUEST_ID.part.part-XXXXXX
```

That file is transport implementation state, not canonical `CTA1` progress. Startup loads and, when
present, verifies the journal before scanning the exact private object-staging tree. It accepts only
canonical lowercase shards and filenames, mode-0700 owner directories on the namespace device, and
mode-0600 owner-owned single-link regular temporary files with a canonical nonzero request ID, six
base-62 suffix bytes, and a size within staging quota. Any malformed or unsafe entry fails closed.
Exact transport temporaries are unlinked and changed shards fsynced; their bytes are never resumed.

Under the namespace transaction recovery then verifies complete CAS and handles every active record
as follows:

- an already present exact CAS object is committed truth and any structurally safe exact staging file
  is removed;
- an exact-size private single-link staging file enters CAS only through the ADR 0247 verified-copy,
  prospective combined-quota commit;
- a strict partial file is removed and the attempt is fenced for a later fresh authorized request;
- absent staging is fenced; and
- unsafe, overlong, linked, corrupt-complete, or otherwise ambiguous state aborts recovery without
  retiring the signed journal.

After all records are classified, recovery clears the active set in one new signed journal mutation.
A crash during recovery is idempotent: already published objects are rediscovered from verified CAS,
and records remain authoritative until the final journal replacement. The recovery result is local
diagnostic truth, not accepted-HEAD or activation authority.

## Nonclaims

`CTA1` by itself does not prove Agent dispatch, remote authorization freshness after restart,
accepted-HEAD-last publication, activation, reachability, repair, quarantine, deletion safety,
power-loss behavior on arbitrary filesystems, or genuine c-toxcore transfer. ADRs 0251/0252 close the
ordinary Agent/native-carrier boundary, and ADR 0267 closes the bounded cap-2/cap-4 client-daemon
restart gate. They do not make `CTA1` a partial-byte resume protocol or a monotonic external witness.
