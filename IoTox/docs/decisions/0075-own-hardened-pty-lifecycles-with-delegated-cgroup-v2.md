# ADR 0075 — Own hardened PTY lifecycles with delegated cgroup v2

- Status: accepted
- Date: 2026-08-18
- Revision: rev0025
- Supersedes: no earlier ADR; strengthens ADRs 0064, 0072, 0073, and 0074

## Context

ADRs 0073 and 0074 made baseline and strict PTY teardown substantially safer: the supervisor pins
process identities with procfs descriptors, start-time witnesses, and pidfds; repeatedly inventories
the helper-created session; and keeps the leader waitable until three complete inventories are empty.
That remains a userspace convergence strategy. It cannot provide the kernel's cgroup-v2 guarantee for
concurrent forks and migration, and it makes completion depend on repeated procfs observations.

Linux cgroup v2 supplies two primitives that match the missing lifecycle boundary:

- writing `1` to a non-threaded cgroup's `cgroup.kill` sends `SIGKILL` to the complete subtree and is
  specified to handle concurrent forks and migration; and
- the recursive `populated` field in `cgroup.events` becomes zero when the cgroup and all descendants
  contain no live process, allowing an empty cgroup to be removed even while a zombie remains
  associated with the deleted cgroup until reap.

Raw cgroup access is safe only inside an explicitly delegated subtree with one manager. systemd's
cgroup delegation guidance calls this the single-writer rule and recommends `Delegate=` on a service
or scope rather than creating children under arbitrary systemd-owned cgroups.

## Decision

### Make cgroup ownership explicit and opt-in

The production PTY factory accepts an optional normalized, absolute, non-root delegated cgroup-v2
path through `--ratox-cgroup-root PATH`. An empty path preserves the rev0024 pidfd/procfs behavior
exactly. A configured path never silently falls back to that behavior.

Before Ratox activation, every enabled profile must use:

- baseline or strict confinement, never compatibility;
- exact credentials;
- a non-root UID distinct from the daemon UID; and
- cleared supplementary groups.

A configured cgroup root cannot be combined with an injected PTY process factory. These checks occur
before transport startup so the daemon cannot advertise a stronger host configuration that its
profile set contradicts.

### Validate and pin the delegated filesystem boundary

The supervisor resolves the configured path descriptor-relatively from `/`, rejects symlinks and
non-normalized components, and requires `CGROUP2_SUPER_MAGIC`. The delegated root, newly created leaf,
and mutation-capable control files must be owned by the daemon UID, must not be group/other writable,
and must not be writable by the configured payload identity.

The root's `cgroup.procs` must be openable for writing, proving that the daemon has the migration
permission required at the common-ancestor boundary. The implementation reads but does not mutate
attributes of the manager-created delegation root.

Each session receives one collision-resistant, underscore-prefixed child name. The underscore avoids
kernel-interface filename collisions. The opened child directory is pinned by device and inode; all
control descriptors are `O_CLOEXEC | O_NOFOLLOW`; cleanup removes only that exact inode.

A new leaf must expose `cgroup.procs`, `cgroup.kill`, `cgroup.events`, `cgroup.type`,
`cgroup.threads`, and `cgroup.subtree_control`; must be a plain `domain`; must contain no process or
thread; must have no enabled child controller; and must report `populated 0`.

### Attach before releasing the sealed helper

The cgroup leaf is created before `posix_spawn`. The helper inherits none of its control descriptors.
After spawn, the parent writes the still-waitable direct child's PID to the leaf's `cgroup.procs` and
requires that the helper is the exclusive initial member and that recursive `populated` becomes one.
Only then does the parent send the sealed manifest that permits child setup and target execution.

The helper is blocked on that manifest during migration, so payload code cannot fork before cgroup
membership is established. The direct child remains waitable, preventing numeric PID reuse during
this sequence.

### Use cgroup kill and recursive quiescence for terminal teardown

For a configured cgroup:

- an explicit KILL request writes `1` to `cgroup.kill` once;
- natural leader exit also starts `cgroup.kill`, so surviving descendants cannot outlive the reported
  terminal completion;
- HUP and TERM retain the identity-pinned pidfd/procfs session sweep because cgroup v2 exposes only
  the subtree-wide SIGKILL primitive;
- the leader remains waitable while `cgroup.events` reports `populated 1`;
- the exact empty cgroup inode is removed before the leader is reaped; and
- startup failure and destructor paths use the same cgroup kill, bounded quiescence, exact removal,
  direct leader/group fallback, and reap sequence.

The parser for `cgroup.events` is bounded and strict: `populated` is mandatory, unique, and Boolean;
`frozen`, when present, is Boolean; duplicate or malformed fields fail closed; unknown numeric
flat-keyed fields remain forward-compatible.

### Preserve the rev0024 fallback contract

When no cgroup root is configured, baseline and strict retain their verified procfs inventory,
pidfd signaling, start-time revalidation, three-empty-sweep rule, and compatibility behavior. This is
an explicit deployment choice, not an implicit downgrade after cgroup failure.

## Consequences

- Configured hardened sessions gain a kernel-owned process subtree, concurrent-fork-aware SIGKILL,
  migration protection during kill, and a recursive completion bit.
- The target identity cannot reach the daemon-owned leaf directory or its mutation controls under the
  validated DAC boundary and cleared supplementary-group contract.
- Every configured host now depends on cgroup v2, a non-threaded domain, `cgroup.kill`, writable
  delegation permissions, and an exclusive single-writer subtree.
- A bad path, ordinary directory, missing interface, incompatible profile, unsafe ownership/mode, or
  failed migration is a named startup/session error; none causes silent fallback.
- Existing deployments remain behaviorally unchanged until the flag is supplied.

## Nonclaims

rev0025 does not claim:

- automatic recovery or garbage collection of leaf directories after an ungraceful daemon crash;
- CPU, memory, I/O, or PID controller quotas;
- protection against another privileged process or same-UID process that violates the delegated
  subtree's single-writer contract;
- a cgroup namespace, mount namespace, container, VM, or complete sandbox;
- qualification on every target kernel, init system, LSM policy, or cgroup mount topology;
- public-network or two-physical-host Ratox qualification; or
- production security certification.

## Executable evidence

The owned registry and native process fixture must prove:

- strict, future-field-compatible `cgroup.events` parsing;
- rejection of missing/duplicate/non-Boolean/malformed cgroup state;
- rejection of inherited, root, and daemon-equal payload identities;
- rejection of an ordinary directory masquerading as cgroup v2;
- rejection of compatibility confinement, relative roots, injected factories, and inherited-profile
  activation before transport startup;
- preservation of every rev0024 pidfd/procfs, capability, seccomp, Landlock, MDWE, descriptor,
  parent-death, restart, authority, and R7 oracle; and
- clean GCC, Clang, release, sanitizer, and static-analysis lanes, subject to the recorded host
  limitations for creating a writable delegated cgroup.

## References

- `docs/research/delegated-cgroup-session-containment-rev0025.md`
- `docs/research/terminal-process-domain-hardening-rev0024.md`
- `docs/terminal-profile-v2.md`
- Linux cgroup v2 documentation: <https://docs.kernel.org/admin-guide/cgroup-v2.html>
- systemd cgroup delegation guidance: <https://systemd.io/CGROUP_DELEGATION/>
- Linux `openat(2)`: <https://man7.org/linux/man-pages/man2/openat.2.html>
- Linux `statfs(2)`: <https://man7.org/linux/man-pages/man2/statfs.2.html>
- Linux `unlinkat(2)`: <https://man7.org/linux/man-pages/man2/unlink.2.html>
