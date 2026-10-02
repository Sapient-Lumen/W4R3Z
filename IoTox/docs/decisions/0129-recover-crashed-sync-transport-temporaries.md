# ADR 0129: recover crashed synchronization transport temporaries

Status: accepted

Date: 2026-08-21

## Decision

A durable synchronization attempt owns both its canonical completed staging path and the exact
private temporary name that `FileTransferManager` may create while receiving into that path. For
attempt `A`, recovery recognizes only:

```text
staging/attempt-<A as 16 lowercase hexadecimal digits>.part
staging/.iotox-attempt-<A as 16 lowercase hexadecimal digits>.part.part-<6 alphanumeric bytes>
```

The signed active-attempt journal is the authority to inspect this attempt-scoped residue. Startup
recovery acquires the namespace transaction, validates the canonical final path and every matching
transport temporary before deleting anything, and accepts at most one exact temporary per attempt.
Every candidate must be an owner-owned, mode-0600, singly linked regular file beneath the strict
owner-private staging directory. A malformed suffix, link, unexpected shape, duplicate matching
temporary, enumeration failure, or removal/fsync failure leaves the signed active record in place
and fails closed.

Once all candidates are validated, recovery removes the exact final staging file and/or exact
transport temporary, fsyncs the staging directory, and only then clears the active journal record.
It does not glob unrelated staging names, infer attempts from filenames, or grant a general garbage
collection entrance.

## Context

The first genuine unclean-restart experiment killed the receiving IoTox daemon while c-toxcore was
delivering an immutable object. The signed attempt journal survived correctly, but the transport had
not yet renamed its private `mkstemp` destination to the canonical attempt path. Recovery therefore
classified canonical staging as absent and fenced the attempt while leaving the transport temporary
behind. Repeated crashes could consume namespace staging quota with unreachable partial files.

ADR 0119 froze the canonical completed staging path, and ADR 0123 made the attempt journal durable,
but neither decision bound the transport's pre-rename name to crash cleanup. This decision closes
that gap without broadening deletion authority.

## Consequences

- A killed receiver cannot ordinarily accumulate unreachable transport partials for a journaled
  attempt; retry begins from a clean staging directory and a new burned attempt ID.
- The first whole-object slice restarts from zero. This is crash recovery, not byte-range resume.
- An unjournaled temporary remains outside this recovery authority. General orphan discovery,
  quarantine, and destructive GC remain separately prohibited.
- Recovery refuses ambiguity rather than deleting a possibly unrelated same-owner file.
- A complete valid canonical staging file still follows ADR 0123's verify-and-commit path; this
  decision concerns incomplete transport state only.

## Evidence

Positive recovery coverage and one new direct refusal check cover exact temporary removal and
hard-link refusal. The owned registry grows from 504 to 505. The complete 26-target GCC/CTest suite
and 41-target Clang 21 ASan/UBSan suite pass; five
delegated-cgroup checks skip in the non-delegated construction shell by design. `nix flake check`
and a clean source-linked product build also pass.

The `sync-file-restart` Sandwurm gate then passed over observed direct UDP and forced TCP. Each cell
rate-shaped an 8 MiB transfer, killed the receiver with status 137 after positive transport progress,
observed two private transport temporaries plus a signed active-attempt journal and no accepted or
activated HEAD, restarted the same IoTox identity, required an empty staging directory after startup
recovery, retried the exact generation-1 revision, and converged plus explicitly activated it. Exact
digests and nonclaims are retained in
`docs/evidence/2026-08-21-sandwurm-sync-restart.md`.
