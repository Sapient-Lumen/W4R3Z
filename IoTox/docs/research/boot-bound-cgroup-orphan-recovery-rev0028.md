# Boot-bound delegated-cgroup orphan recovery — rev0028

**Research date:** 2026-08-18  
**Applied revision:** rev0028  
**Decision:** `../decisions/0079-bind-delegated-cgroup-lifecycles-to-boot-and-process-incarnations.md`

## Question

How can an IoTox daemon safely reclaim a populated terminal cgroup left by an ungraceful predecessor
without trusting a reusable PID, crossing boot boundaries, racing another legitimate startup, or
turning a malformed delegated namespace into partial destructive cleanup?

## Primary interfaces reviewed

The review rechecked the following primary Linux interface documentation online:

```text
https://docs.kernel.org/admin-guide/cgroup-v2.html
https://docs.kernel.org/admin-guide/sysctl/kernel.html
https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
https://man7.org/linux/man-pages/man2/pidfd_open.2.html
https://man7.org/linux/man-pages/man2/poll.2.html
```

The cgroup-v2 documentation establishes that `cgroup.kill` recursively kills processes in a cgroup
subtree and that `cgroup.events` `populated` describes whether the cgroup or descendants contain live
processes. The kernel sysctl documentation identifies `boot_id` as the random UUID generated once per
boot. `proc_pid_stat(5)` defines task state and field 22 as start time after system boot.
`pidfd_open(2)` supplies a process handle whose readiness reports process exit; `poll(2)` defines the
nonblocking readiness check used in classification.

The sources define kernel contracts. They do not establish IoTox's pathname ownership, startup order,
scan bounds, or preflight rules; those are construction decisions retained in ADR 0079.

## Applied identity model

A safe reclaim decision needs an exact historical creator identity rather than a numeric PID. rev0028
therefore names every new leaf:

```text
_iotox_session_v2_<32-lowercase-boot-id-hex>_<pid>_<start-time-ticks>_<sequence>
```

The witnesses serve different purposes:

| Witness | Prevents |
|---|---|
| canonical boot ID | treating a prior-boot PID/start value as current |
| positive numeric PID | locating the possible current creator process |
| procfs field-22 start time | same-boot PID reuse |
| pidfd plus nonblocking poll | classifying the exact current PID occupant through a stable handle |
| local sequence | basename collision among sessions from one daemon incarnation |

No single witness is sufficient. Boot ID plus PID misses same-boot reuse. PID plus start time misses
cross-boot reuse. A basename alone cannot prove the current process still matches. A pidfd opened from
a numeric PID must be surrounded by pinned procfs identity reads so the classification is coherent.

## Applied startup ordering

Static terminal configuration remains checked before persistent mutation. When a delegated root is
configured, startup then performs:

```text
validate profile/helper/identity/path shape
acquire signed device-bound Ratox host-incarnation lease
open and preflight procfs plus the delegated cgroup-v2 root
recover the complete bounded reserved-name set
construct the production PTY factory
publish local service and start toxcore/network work
```

The signed host lease is the existing durable legitimate-daemon serialization point. Moving recovery
inside that lease prevents two valid IoTox starts from concurrently classifying or mutating leaves. It
does not defend against root or an external writer with equivalent delegated-root authority.

## Applied filesystem and mutation boundary

Recovery opens the real procfs and cgroup-v2 filesystems with no-follow, descriptor-relative
operations. Each candidate is pinned to its inode and validated as the expected daemon-owned,
restrictive, one-level domain leaf with no child cgroups and no controller/thread state that violates
the session contract.

The candidate set is bounded and fully preflighted before mutation. This matters because a streaming
"inspect then kill" loop could reclaim an early stale subtree and only later encounter a malformed
reserved name, producing a partial recovery that the caller could not reason about atomically. After
`cgroup.kill`, the implementation polls the already-read `cgroup.events` descriptors as one bounded
set and re-reads complete records on notification; it does not spin on one-millisecond sleeps.

After preflight:

- exact live versioned owner: preserve;
- proved-stale versioned owner: `cgroup.kill`, wait on kernel `cgroup.events` notifications for
  recursive `populated 0`, revalidate exact pathname/inode identity, remove;
- empty legacy PID-only leaf: remove without killing anything;
- populated legacy PID-only leaf: refuse startup;
- malformed reserved-prefix leaf: refuse startup.

Unverifiable evidence is not stale evidence. Parse failures, inaccessible procfs data, changed inodes,
unsupported controls, invalid ownership/mode, unexpected children, and quiescence timeout all fail
startup.

## Bounds and observability

The public recovery configuration constrains candidate count to `1..1024` and quiescence wait to a
positive value no greater than 30 seconds. Runtime status publishes only aggregate counts:

```text
reserved names observed
live exact incarnations preserved
stale exact incarnations classified
stale exact incarnations recovered
empty legacy leaves removed
```

It publishes no boot ID, PID, cgroup pathname, profile content, terminal data, command data, or error
payload.

## Executable evidence

The direct registry adds parser, identity, configuration, filesystem, lifecycle-ordering, and Agent
serialization checks. A separate process oracle uses `unshare -UrCm`, mounts a fresh cgroup-v2
hierarchy, and proves with kernel state rather than an ordinary-directory double:

1. a live exact owner is preserved;
2. a deliberately crashed creator leaves a populated versioned leaf;
3. restart recovery recursively kills the surviving payload;
4. `cgroup.events` reaches `populated 0` and the exact leaf is removed;
5. an empty legacy leaf is removed;
6. a populated legacy leaf is refused and preserved;
7. a malformed reserved name blocks recovery; and
8. exceeding the candidate bound causes no premature mutation.

The CTest route uses skip code 77 only when the host denies the required user, mount, or cgroup
namespace construction. It never substitutes a synthetic cgroup positive.

## Resulting boundary

rev0028 closes the specifically named rev0025 crash-orphan collection gap for versioned leaves while
preserving fail-closed behavior for unsafe legacy state. It does not add cgroup resource limits,
namespace isolation, PTY state persistence, storage rollback protection, power-cut qualification,
protection from a competing privileged manager, target-fleet qualification, or production approval.
