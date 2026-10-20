# Delegated cgroup-v2 PTY-session containment — rev0025

**Research date:** 2026-08-18 America/New_York  
**Applied revision:** rev0025  
**Decision:** ADR 0075

## Question

Can IoTox replace the strongest remaining userspace PTY teardown approximation with an optional,
fail-closed kernel-owned lifecycle boundary without silently changing existing deployments or
pretending that raw access to an arbitrary cgroup path is safe delegation?

## Primary-source findings

### `cgroup.kill` is stronger than a procfs convergence loop

The Linux cgroup-v2 documentation defines `cgroup.kill` on non-root cgroups. Writing `1` kills the
cgroup and all descendants with SIGKILL; the kernel explicitly states that the operation handles
concurrent forks and is protected against migration. A threaded cgroup rejects the operation, so the
IoTox leaf must remain a plain process-domain cgroup.

rev0024's repeated procfs sweeps remain useful for graceful HUP/TERM and for hosts that do not opt in,
but they are not equivalent to this kernel primitive. rev0025 therefore routes only KILL through the
cgroup and keeps the prior identity-pinned session sweep for nonfatal signals.

### `cgroup.events: populated` is the recursive completion witness

For each non-root cgroup, `cgroup.events` contains a recursive Boolean `populated` field. It is one
while the cgroup or any descendant contains a live process and zero after the complete subtree has no
live process. The documentation also states that zombies do not appear in `cgroup.procs` and that a
cgroup associated only with zombies is empty and removable.

This permits the required order:

```text
observe waitable leader exit or receive explicit KILL
  -> write 1 to cgroup.kill
  -> retain the waitable leader identity
  -> require recursive populated 0
  -> remove the exact cgroup inode
  -> reap and report the leader's original status
```

No empty procfs scan is promoted into an atomic claim.

### Delegation requires an exclusive subtree, not an arbitrary path

systemd's delegation guidance identifies a single-writer rule: one manager owns each cgroup subtree.
It directs services and scopes to use `Delegate=` and says systemd then leaves descendants under the
delegated point to the program. For `User=` services, the subtree is chowned so the service can create
children. The guidance also warns against creating cgroups beneath arbitrary systemd-managed nodes
and recommends underscore-prefixing names that might collide with kernel interface files.

rev0025 accepts only an administrator-supplied absolute path. It opens each path component without
following symlinks, requires cgroup-v2 filesystem magic, and validates daemon ownership and restrictive
modes on the root, leaf, and mutation-capable interface files. It does not infer systemd unit names,
write root attributes, require systemd, or treat the optional `user.delegate` xattr as a portable
kernel contract.

### Migration permission has a common-ancestor condition

The kernel delegation rules require write access to the destination `cgroup.procs` and to
`cgroup.procs` at the common ancestor of source and destination. IoTox opens the configured root's
`cgroup.procs` for writing during validation and opens the new leaf's `cgroup.procs` read/write. The
actual helper migration is still the definitive operation and fails closed if outer topology, LSM
policy, or delegation permissions reject it.

### Attach-before-manifest closes the payload fork window

`posix_spawn` initially creates the helper in the daemon's cgroup. The parent creates and pins the
leaf first, spawns the sealed helper, moves the still-waitable direct child into the leaf, verifies
exclusive membership plus `populated 1`, opens the child pidfd, and only then sends the manifest. The
helper cannot execute target code before receiving that manifest.

This is not `clone3(CLONE_INTO_CGROUP)`: the project retains `posix_spawn` because the Agent can be
multithreaded and its existing helper protocol avoids an unsafe post-fork C++ child path. The bounded
pre-manifest interval is explicitly retained as a migration interval, not hidden as zero jitter.

## Construction

### Root and leaf validation

- require a normalized absolute path other than `/`;
- walk from an open `/` descriptor with `openat`, `O_DIRECTORY`, `O_NOFOLLOW`, and `O_CLOEXEC`;
- require `fstatfs(...).f_type == CGROUP2_SUPER_MAGIC`;
- require daemon-UID ownership and reject group/other write bits;
- reject any boundary writable by the exact payload UID/GID;
- require writable root `cgroup.procs` permission without mutating the delegated root;
- create `_iotox_session_<daemon-pid>_<monotonic-sequence>` with bounded collision retries;
- pin the leaf device/inode and remove only an exact revalidated match;
- require `cgroup.type == "domain\n"`;
- require empty `cgroup.procs`, empty `cgroup.threads`, empty `cgroup.subtree_control`, and
  `populated 0`; and
- require usable `cgroup.kill` before the helper exists.

All root and leaf descriptors are close-on-exec. The payload receives no cgroup control descriptor.

### Profile and daemon constraints

A configured root is accepted only for enabled baseline/strict profiles with exact non-root UIDs
that differ from the daemon UID and with supplementary groups cleared. The target UID therefore does
not own the daemon's cgroup boundary, and its primary group is checked against each write bit. The
existing baseline/strict seccomp policy additionally denies session/namespace mutation and
process-handle acquisition inside the final payload.

Compatibility profiles keep their historical process-group contract and cannot claim delegated
containment. An injected test/factory implementation cannot claim that the production cgroup path was
used.

### Teardown

- `ProcessSignal::kill` writes `1\n` once to the pinned `cgroup.kill` descriptor.
- Polling after natural leader exit initiates the same kill if no explicit KILL occurred.
- While recursive `populated` is one, exit remains unreported and the leader remains waitable.
- At zero, the pinned pathname is revalidated by device/inode, all leaf controls are closed, and
  `unlinkat(..., AT_REMOVEDIR)` removes the cgroup.
- The leader is then reaped and its exact exit kind/code/core flag is returned.
- Startup failure and object destruction use a bounded best-effort version of the same sequence, then
  retain direct group/leader SIGKILL as an emergency fence.

## Parser and resource bounds

The `cgroup.events` reader accepts at most 64 KiB. Every line must be one lowercase flat key, one
space, one unsigned decimal value, and one newline. Duplicate keys, missing `populated`, signs,
blank lines, nondecimal values, and non-Boolean known fields are rejected. Unknown numeric keys are
retained as forward-compatible syntax but ignored semantically.

Cgroup names use at most 1,024 collision attempts. Destructor waiting is clamped to five seconds and
normal PTY cleanup requests 250 ms before preserving the exact cgroup for administrator-visible
recovery if the kernel still reports a live subtree.

## Executable evidence and host limitation

The revision adds seven parser/identity/filesystem registry checks, one Agent activation check, and a
native POSIX-process fail-closed check. The direct owned registry is now 303 checks; the default suite
remains fourteen CTest targets.

The qualification container exposes a genuine cgroup-v2 mount at `/sys/fs/cgroup`, but the mount is
read-only and the container lacks a delegated writable subtree. The negative filesystem-magic and
configuration paths execute here; a positive live migration/kill/populated lifecycle cannot be
honestly manufactured without changing the host's cgroup delegation. The source therefore records
that lane as externally required rather than labeling it green.

## Operator shape

A systemd deployment should allocate an exclusive service/scope delegation and pass the actual path
made available to the daemon. A representative unit concept is:

```ini
[Service]
Delegate=yes
# On newer systemd, DelegateSubgroup=supervisor may place the daemon below the
# delegated root. The exact cgroup path must be supplied by deployment logic.
ExecStart=/usr/local/bin/iotox run ... --ratox-cgroup-root /sys/fs/cgroup/.../iotox.service
```

The example is explanatory, not a portable path-discovery algorithm. Unit-name-to-path translation is
not treated as stable systemd API.

## Nonclaims

rev0025 does not claim:

- crash-restart cleanup of abandoned `_iotox_session_*` directories;
- resource-controller limits or accounting policy;
- defense against root, kernel compromise, or another same-UID writer violating delegation;
- direct creation with `CLONE_INTO_CGROUP` or zero migration jitter;
- a cgroup namespace, container, or complete syscall allowlist;
- qualification across the target fleet or every LSM/init configuration;
- public-network or two-physical-host Ratox qualification; or
- production security certification.

## Sources rechecked online

```text
https://docs.kernel.org/admin-guide/cgroup-v2.html
https://systemd.io/CGROUP_DELEGATION/
https://man7.org/linux/man-pages/man2/clone.2.html
https://man7.org/linux/man-pages/man2/openat.2.html
https://man7.org/linux/man-pages/man2/statfs.2.html
https://man7.org/linux/man-pages/man2/unlink.2.html
```

These sources define Linux and systemd interface semantics. They do not audit IoTox or prove its
security. The executable evidence establishes only the bounded behavior described above, and the
positive delegated-cgroup lifecycle remains a required target-host qualification lane.
