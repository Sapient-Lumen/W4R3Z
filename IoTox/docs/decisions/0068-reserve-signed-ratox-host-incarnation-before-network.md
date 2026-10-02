# ADR 0068: Reserve a signed Ratox host incarnation before network startup

Status: accepted
Date: 2026-08-17

## Context

Ratox attachment identity includes a host incarnation so packets from an old process cannot be
retargeted to a replacement PTY. A constant or process-local incarnation is insufficient across
daemon restart: a successor could reuse the former value, and two concurrently started daemons could
both advertise the same durable namespace. The reservation must complete before toxcore or the local
terminal listener can advertise Ratox support.

The state path is security-sensitive. Pathname checks followed by ordinary opens permit substitution;
a write followed by rename is not durable across a crash unless both the file and containing
directory are synchronized; and Linux `flock` is advisory rather than an integrity mechanism.

Primary Linux references rechecked for this decision:

```text
https://man7.org/linux/man-pages/man2/open.2.html
https://man7.org/linux/man-pages/man2/flock.2.html
https://man7.org/linux/man-pages/man2/rename.2.html
https://man7.org/linux/man-pages/man2/fsync.2.html
https://man7.org/linux/man-pages/man7/path_resolution.7.html
https://man7.org/linux/man-pages/man2/close.2.html
```

## Decision

An explicitly enabled Ratox host acquires one `RatoxIncarnationLease` before constructing the live
service, terminal listener, or transport. Client-only activation acquires no lease.

### Durable record

The state is one exact 128-byte `IOTXRIN1` record:

```text
magic/version/algorithm
stable device signing public key
nonzero 64-bit incarnation
bitwise complement of incarnation
Ed25519 signature over the first 64 bytes
```

The first value is random, nonzero, and restricted below the top bit. Every later successful
reservation is exactly the prior value plus one. Zero, malformed records, wrong identity, signature
failure, complement failure, and wraparound fail closed.

### Path and file contract

The default path is `<savedata-parent>/ratox/incarnation.state`. The implementation traverses path
components with descriptor-relative `openat` and `O_NOFOLLOW`, rejects `..`, and creates missing
components at exact mode `0700`. The final directory must be a same-euid directory at exact mode
`0700`; the state and lock must be same-euid, single-link regular files at exact mode `0600`.
Symlink, hard-link, type, owner, mode, size, and path/inode substitution failures are rejected.
Existing path components are never permission-repaired after another actor wins a creation race.
Each directory created by the reservation transaction is fsynced after exact-mode enforcement, then
its containing directory is fsynced before traversal continues. This separately persists the new
directory inode metadata and the directory entry naming it; synchronizing only the final state file
would not make a newly created hierarchy durable.

### Exclusion and commit

A sibling lock file is held with nonblocking exclusive `flock` for the lifetime of the host service.
The lock prevents cooperating IoTox processes from sharing the namespace; it is not treated as an
integrity boundary. The signed record and strict inode checks remain authoritative.

The successor record is written to a private descriptor-relative temporary file, synchronized,
atomically installed with `renameat`, followed by containing-directory `fsync`, then reopened and
strictly decoded before the lease is returned. Linux `close(EINTR)` is never retried because the file
descriptor may already have been released and reused. `fsync` and hierarchy-creation interruption are
retried before classification.

### Service and diagnostic contract

The reserved value is injected into every successful Ratox OPEN result. Runtime status publishes only
`ratox-host-incarnation` and `ratox-incarnation-lease-held`; terminal bytes, paths, profile identifiers,
and error payloads remain outside persistent Ratox lifecycle evidence. Cleanup releases the lease
after Ratox shutdown. A startup failure remains durably projected as `phase=failed` rather than being
rewritten to `stopped` by destruction.

The transport-independent service configuration defaults to incarnation zero. Disabled construction
remains valid, but an enabled direct caller is invalid until it explicitly supplies a nonzero reserved
lease value. This prevents accidental fixed-incarnation reuse outside the Agent constructor.

A silent local client may not hold the sole pre-OPEN terminal attachment indefinitely. The private
`SOCK_SEQPACKET` server enforces a bounded first-packet deadline and emits a typed connection-scoped
error before admitting a successor.

## Consequences

A cooperating second daemon cannot advertise the same Ratox host incarnation. A clean successor
advances exactly once, while a rejected contender cannot mutate the record. Old attachment packets
therefore cannot acquire authority over a replacement service merely because the daemon restarted.

The record detects accidental corruption, wrong-device reuse, and unprivileged substitution under the
owner-private lane. It does not prevent a privileged attacker, filesystem rollback, VM snapshot
restore, storage firmware failure, or an actor that ignores the advisory lock and can write as the
owner. Hardware rollback protection and crash/power-cut qualification remain separate work.

This decision intentionally does not preserve a PTY or controller replay state across daemon restart.
The current restart contract terminates those process-local objects; a future supervised-child design
would require its own durable input-commit protocol and ADR.

## Rejected alternatives

- **Use process ID or wall clock as the incarnation.** Both can repeat and neither proves durable
  monotonic succession.
- **Increment after networking starts.** That creates an advertisement window with ambiguous
  attachment identity.
- **Trust only `flock`.** The lock is advisory and says nothing about record identity or pathname
  substitution.
- **Rewrite the state file in place.** A crash can leave a torn record and rename durability still
  requires explicit directory synchronization.
- **Automatically chmod existing directories/files.** That can repair an attacker-controlled object
  after a race and hides configuration drift.
- **Claim restart-persistent PTYs from a host counter.** Incarnation fencing and process supervision
  are different contracts.
