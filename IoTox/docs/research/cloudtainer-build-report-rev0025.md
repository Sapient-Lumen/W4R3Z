# IoTox cloudtainer build report — rev0025

**Date:** 2026-08-18 America/New_York
**Version:** 0.25.0
**Revision:** rev0025
**Codename:** Delegated Cgroup Kill-Quiescence Citadel
**Linked handoff revision:** rev0012

## Outcome

rev0025 materially strengthens the optional Linux PTY lifecycle boundary without changing default
activation. A host may now supply one explicit delegated cgroup-v2 root with
`--ratox-cgroup-root PATH`. For every baseline or strict PTY, the production supervisor creates one
private cgroup leaf, attaches the still-blocked helper before releasing its manifest, uses the
kernel's subtree-wide `cgroup.kill` primitive for final teardown, waits for recursive
`cgroup.events` `populated=0`, removes the exact pinned leaf, and only then reaps the waitable leader.
Empty configuration preserves rev0024's pidfd/procfs supervision exactly.

The implementation, documentation, compiler matrix, sanitizer matrix, static-analysis lanes, native
process oracles, and 303-check owned registry all pass in this qualification container. The host has a
genuine cgroup-v2 filesystem but mounts `/sys/fs/cgroup` read-only and exposes no writable delegated
subtree. Consequently, the positive live cgroup create/attach/kill/remove path was not executed here.
The revision claims its parser, policy, pre-network validation, ordinary-path refusal, and named
fail-closed behavior on this host; positive lifecycle success remains a required target-host lane.

## Online primary-source review

The following primary references were rechecked online on 2026-08-18:

```text
https://docs.kernel.org/admin-guide/cgroup-v2.html
https://systemd.io/CGROUP_DELEGATION/
https://man7.org/linux/man-pages/man2/clone.2.html
https://man7.org/linux/man-pages/man7/cgroups.7.html
https://man7.org/linux/man-pages/man2/openat.2.html
https://man7.org/linux/man-pages/man2/statfs.2.html
https://man7.org/linux/man-pages/man2/unlink.2.html
```

The Linux cgroup-v2 documentation defines hierarchical process membership, `cgroup.kill`, recursive
`cgroup.events` population state, child naming conventions, and cgroup-v2 filesystem identity. The
systemd guidance defines delegated-subtree ownership and the single-writer rule. The syscall manuals
inform descriptor-relative path walking, filesystem verification, exact removal, and the future
`CLONE_INTO_CGROUP` option. These references define interfaces; they do not audit IoTox or establish
its security.

The applied design review is retained in
`docs/research/delegated-cgroup-session-containment-rev0025.md`, and the accepted contract is ADR 0075.

## Constructed lifecycle boundary

### Explicit, default-off host selection

`Agent::InteractiveConfig` and `PosixPtyOptions` now carry an optional delegated root. The CLI exposes
it as `--ratox-cgroup-root PATH`. Empty configuration does not create, inspect, or claim a cgroup
boundary.

When configured, Agent activation rejects malformed roots, injected PTY factories, compatibility
profiles, inherited identities, root identities, daemon-equal identities, and identities that retain
supplementary groups. The production factory repeats the security-critical checks at spawn so direct
callers cannot bypass the Agent gate.

### Descriptor-relative delegation validation

`SessionCgroup::create` walks the normalized absolute root component by component from `/` with
`openat`, `O_DIRECTORY`, `O_CLOEXEC`, and `O_NOFOLLOW`. It requires `CGROUP2_SUPER_MAGIC`, daemon
ownership, no group/other write authority, no write authority for the exact payload UID/GID, and an
openable root `cgroup.procs` migration boundary.

Every session receives one underscore-prefixed `_iotox_session_<daemon-pid>_<sequence>` child. The
underscore follows the cgroup-v2 user-child naming convention and avoids collisions with kernel
interface filenames. Name creation is bounded to 1,024 attempts.

### Immediate pathname and inode pinning

A failure-path review found that a leaf created successfully but failing before ordinary descriptor
capture needed a stronger cleanup witness. The final implementation therefore calls `fstatat` with
`AT_SYMLINK_NOFOLLOW` immediately after `mkdirat`, records device and inode before opening any child
control file, and compares the later opened directory descriptor against that exact witness.

This lets every subsequent construction failure remove only the leaf IoTox created when its pathname
still names the pinned inode. A same-name replacement is refused rather than followed or removed.
All leaf control descriptors are close-on-exec and no-follow.

### Leaf shape and authority checks

A usable leaf must expose and protect:

```text
cgroup.procs
cgroup.kill
cgroup.events
cgroup.type
cgroup.threads
cgroup.subtree_control
```

The leaf must be a plain `domain`, contain no processes or threads, enable no child controllers, and
report `populated 0`. Required control files must remain daemon-owned and non-writable by the payload
identity. Missing controls, read-only interfaces, ownership mismatch, malformed records, unexpected
population, or incompatible topology fail closed.

### Attach before target setup

The parent creates the leaf before `posix_spawn`. The one-binary helper blocks waiting for its sealed
manifest. Before sending that manifest, the parent writes the waitable helper PID to the leaf's
`cgroup.procs`, reads membership back, requires the helper to be the exclusive initial member, and
requires recursive `populated=1`.

Payload code therefore cannot fork before cgroup membership is established. The direct child remains
waitable throughout the transition, preserving its numeric identity while the cgroup and pidfd
witnesses are acquired.

### Kernel kill and recursive completion

HUP and TERM retain the descriptor-relative procfs/pidfd session sweep because cgroup v2 provides a
subtree-wide SIGKILL primitive rather than arbitrary subtree signals. Explicit final KILL writes `1`
to `cgroup.kill`. Natural leader exit starts the same kill so descendants cannot outlive terminal
completion.

The supervisor retains the leader as a waitable zombie while `cgroup.events` reports any live process
in the leaf or descendants. Once recursive `populated=0` is observed, it revalidates the leaf pathname
against the pinned device/inode, removes that exact empty leaf, and then reaps the leader while
preserving its exit status. Startup-failure and destructor paths use bounded cgroup kill/quiescence
plus direct leader/group fallback and reap.

## Parser and failure behavior

The cgroup-events parser is bounded to 64 KiB. It requires one LF-terminated flat key/value pair per
line, unique valid keys, unsigned canonical decimal values, and exactly one Boolean `populated` field.
Optional `frozen` is also Boolean. Unknown future numeric fields are accepted; duplicate, malformed,
missing, signed, overflowing, or non-Boolean state fails closed.

The implementation classifies missing kernel interfaces/topology as unsupported, permissions and
read-only delegation as unavailable, bounded namespace/storage exhaustion as resource exhaustion, and
malformed kernel-facing records as protocol errors. A requested cgroup boundary never silently falls
back to procfs-only lifecycle semantics.

## Executable evidence

### Owned C++ registry

The direct GCC Debug registry passed **303/303** checks. Eight checks are new at this boundary:

- strict canonical and future-field-compatible `cgroup.events` parsing;
- missing, duplicate, non-Boolean, and ambiguous record refusal;
- inherited, root, and daemon-equal payload identity refusal;
- ordinary-directory refusal as non-cgroup v2; and
- Agent pre-network rejection of relative roots, injected factories, and inherited enabled profiles.

The complete previous authority, restart, protocol, PTY, confinement, descriptor, procfd, process
hardening, telemetry, file-transfer, transport, runtime-tree, and R7 evidence remains green.

### Native PTY process oracle

The native production-factory test requires configured containment to refuse an inherited identity,
a compatibility profile, and an ordinary directory masquerading as cgroup v2. The complete baseline
and strict process tests remain green, including pidfd/procfs support, argument-aware seccomp,
capability clearing, securebits/bounding-set behavior where privileged, descriptor closure,
parent-death handling, repeated quiescence, fork-churn convergence, natural-leader cleanup, and strict
success-or-named-fail-closed behavior.

The GCC Release native PTY process target passed once and then **30/30** consecutive repeat runs.

### Compiler and test matrix

```text
GCC 14.2 Debug warnings-as-errors build:          PASS
GCC 14.2 Debug CTest:                             14/14
Direct owned registry:                            303/303
Clang 17 Debug warnings-as-errors build:          PASS
Clang 17 Debug CTest:                             14/14
GCC 14.2 Release warnings-as-errors build:        PASS
GCC 14.2 Release CTest:                           14/14
GCC Release native PTY repetition:                30/30
Clang 17 ASan+UBSan warnings-as-errors build:     PASS
Clang ASan+UBSan owned shards:                    16/16
Clang ASan+UBSan remaining process/analyzer:      13/13
GCC 14.2 ThreadSanitizer warnings-as-errors build: PASS
GCC TSan owned shards:                            16/16
GCC TSan remaining process/analyzer:              13/13
Sanitizer runtime diagnostic scan:                none
Clang static analyzer, terminal_cgroup.cpp:       PASS
Clang static analyzer, terminal_posix.cpp:        PASS
Clang static analyzer, agent.cpp:                 PASS
Python tool bytecode compilation:                 PASS
Ratox R7 analyzer self-test:                      PASS
CLI cgroup option presence:                       PASS
Product identity:                                 IoTox 0.25.0 rev0025
```

The sanitizer presets split the same 303-check owned registry into sixteen deterministic shards. The
reported 29 unique sanitizer tests are those sixteen shards plus thirteen non-registry process and
analyzer targets; they are not 29 additional product checks.

## Qualification-host facts

```text
kernel: Linux 6.18.35 x86_64
cgroup filesystem: cgroup2fs, magic 0x63677270
/sys/fs/cgroup mount: ro,nosuid,nodev,noexec,relatime,nsdelegate
writable delegated subtree available to this run: no
self cgroup: 0::/
```

The genuine filesystem identity supports the ordinary-path distinction and documents the target
interface. The read-only mount prevents truthful creation of a delegated leaf. No mock filesystem,
bind-mounted ordinary directory, privileged remount, or invented positive result was substituted.

## Evidence inventory

Revision-owned evidence is retained under `artifacts/rev0025/`, including:

- toolchain, kernel, and cgroup mount identity;
- online source inventory;
- clean configure/build/test logs and exit files for GCC Debug, Clang Debug, GCC Release,
  Clang ASan+UBSan, and GCC TSan;
- verbose 303-check registry output;
- native PTY repetition output;
- three static-analyzer logs;
- Python and R7 self-test output;
- product identity and CLI help evidence;
- sanitizer diagnostic scan;
- source-integrity record; and
- this report's validation summary and checksums.

## Nonclaims and remaining work

rev0025 does not claim:

- a positive delegated-cgroup lifecycle run in this read-only container;
- automatic discovery or removal of cgroup leaves after ungraceful daemon death;
- CPU, memory, I/O, or PID controller quotas or accounting policy;
- protection against another privileged or same-UID manager violating the delegated subtree's
  single-writer contract;
- use of `CLONE_INTO_CGROUP` or elimination of the blocked-helper migration interval;
- a PID, user, mount, network, or cgroup namespace sandbox;
- a read/execute allowlist, mount isolation, container, VM, or complete syscall allowlist;
- every target kernel, service manager, LSM, outer sandbox, or cgroup topology;
- PTY survival across daemon restart;
- public-network or two-physical-host R7 qualification; or
- production security certification or readiness.

The next cgroup-specific qualification lane is a named writable `Delegate=` host or equivalent
single-writer delegation. It must execute successful create/attach/fork/kill/populated/remove paths,
exercise startup and natural-exit failures, verify no residual leaves, and retain exact kernel,
service-unit, ownership, mount, and process evidence. Resource policy, crash orphan collection, and
possible `CLONE_INTO_CGROUP` adoption remain separate reviewed changes.
