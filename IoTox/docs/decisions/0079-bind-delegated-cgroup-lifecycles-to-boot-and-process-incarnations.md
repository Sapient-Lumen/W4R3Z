# ADR 0079: Bind delegated cgroup lifecycles to boot and process incarnations

- Status: accepted and implemented
- Date: 2026-08-18
- Revision: rev0028
- Extends: ADR 0068 signed host-incarnation reservation, ADR 0074 pinned process identity, and ADR 0075 delegated cgroup-v2 lifecycle ownership

## Context

ADR 0075 gives each hardened PTY one daemon-owned cgroup-v2 domain leaf, moves the still-waitable
helper into that leaf before manifest release, uses recursive `cgroup.kill`, waits for
`cgroup.events: populated 0`, and removes the exact inode during orderly teardown. That construction
owned a running session well, but the original `_iotox_session_<pid>_<sequence>` basename did not
carry enough identity to authorize cleanup after an ungraceful daemon exit.

A numeric PID is reusable and restarts cross boot boundaries. After a crash, a later daemon could not
safely infer that a populated PID-only leaf belonged to a dead predecessor. Leaving every abandoned
leaf untouched was fail closed but leaked payload processes and delegated namespace entries. Killing a
leaf merely because its numeric PID was absent at one instant would create a PID-reuse and startup-race
hazard. Two legitimate IoTox daemon starts could also race while inspecting and mutating the same
delegated root unless recovery was serialized by an already durable authority.

Linux exposes the required witnesses:

- `/proc/sys/kernel/random/boot_id` identifies the running kernel boot;
- `/proc/<pid>/stat` field 22 identifies a process start time within that boot;
- `pidfd_open(2)` supplies a pollable handle to the process currently occupying a numeric PID;
- cgroup v2 `cgroup.kill` kills every process in a subtree, including descendants; and
- `cgroup.events` reports recursive `populated` state for teardown completion.

These witnesses can classify an exact creator incarnation without trusting a reusable PID alone.
They do not make a cgroup pathname authoritative by themselves, so descriptor-relative filesystem,
ownership, type, mode, and inode checks remain mandatory.

## Decision

### Versioned owner-incarnation names

Every newly created delegated terminal leaf SHALL use this canonical basename:

```text
_iotox_session_v2_<boot-id-hex>_<pid>_<start-time-ticks>_<sequence>
```

Where:

- `<boot-id-hex>` is exactly 32 lowercase hexadecimal characters derived from the canonical Linux
  boot UUID after removing hyphens;
- `<pid>` is the creating daemon's positive numeric PID;
- `<start-time-ticks>` is the unsigned decimal field-22 value read from the creating daemon's pinned
  procfs process directory; and
- `<sequence>` is the existing positive local collision-avoidance sequence.

The parser SHALL reject noncanonical case, width, separators, signs, overflow, zero PID, zero start
witness, zero sequence, trailing bytes, and every reserved-prefix name it cannot interpret exactly.
No payload or remote protocol field changes.

### Serialize recovery with the signed host lease

An enabled Ratox terminal host SHALL acquire the durable, signed, device-bound host-incarnation lease
from ADR 0068 before it scans or mutates the delegated cgroup root. Static profile, helper, identity,
and path-shape validation may run first, but the following order is mandatory:

1. validate non-mutating terminal configuration;
2. acquire the exact Ratox host-incarnation lease;
3. recover the bounded delegated-cgroup namespace;
4. construct the production PTY factory; and
5. advertise local listeners or start network service.

A competing legitimate daemon therefore fails on the existing lease and cannot perform concurrent
recovery. Lease acquisition does not authorize an arbitrary same-UID or privileged writer; the
administrator must still preserve the cgroup-v2 single-writer delegation contract.

### Pin procfs and cgroup identity

Recovery SHALL open the real procfs and delegated cgroup-v2 roots without following symlinks and
SHALL validate their filesystem magic before trusting content. Every reserved candidate SHALL be
opened descriptor-relatively, pinned to an inode, and preflighted for:

- daemon ownership and the configured restrictive mode contract;
- cgroup-v2 filesystem identity;
- one-level domain cgroup type;
- empty subtree-controller and thread-state surfaces required by the session contract;
- absence of child cgroups; and
- exact basename grammar.

The complete bounded candidate set SHALL pass preflight before the first kill or removal. Recovery
must not partially mutate an earlier candidate and then discover an unverifiable later one.

### Classify an exact owner incarnation

For a versioned leaf, recovery SHALL:

1. compare its boot witness with the current canonical boot ID;
2. open `/proc/<pid>` descriptor-relatively through verified procfs;
3. parse and retain field 22 and task state from that pinned directory;
4. obtain a pidfd for the process occupying the numeric PID;
5. re-read the same pinned process identity after pidfd acquisition; and
6. poll the pidfd nonblockingly before declaring the owner live.

The owner is live only when the boot ID, PID, pre/post start-time witnesses, nonterminal task state,
and pidfd liveness all agree. Boot mismatch, process absence, start-time mismatch, or terminal task
state classifies the named creator as stale. Malformed or unreadable evidence is an error and never
authorizes cleanup.

### Recover only proved-stale leaves

Recovery SHALL inspect no more than the configured candidate limit, constrained to `1..1024`, and
SHALL use a finite recursive-quiescence wait constrained to `(0, 30 seconds]`.

After full preflight:

- exact live versioned owners are preserved;
- proved-stale versioned leaves receive `cgroup.kill`, wait through kernel `cgroup.events`
  `poll(2)` notifications until recursive `populated 0`, have their pathname/inode identity
  revalidated, and are removed;
- empty legacy `_iotox_session_<pid>_<sequence>` leaves may be removed because no process is harmed;
- populated legacy leaves fail startup because their PID-only names cannot retrospectively defeat PID
  reuse; and
- malformed reserved-prefix entries fail startup.

A timeout, changed inode, unexpected child, unsupported control, ownership/mode change, parse error,
or other inconsistency aborts startup. Configured recovery never silently falls back to procfs-only
supervision.

### Publish content-free evidence

The runtime snapshot SHALL expose only aggregate counters for reserved names observed, exact live
incarnations preserved, stale incarnations classified, stale incarnations recovered, and empty legacy
leaves removed. A populated legacy leaf fails startup and therefore produces no successful recovery
snapshot. Status SHALL not expose boot IDs, PIDs, paths, command data, terminal bytes, or profile
content.

## Consequences

### Positive

- A daemon restart can reclaim payloads and cgroup leaves abandoned by a crashed versioned creator
  without authorizing action from a numeric PID alone.
- Cross-boot leftovers are unambiguously stale.
- Same-boot PID reuse is fenced by procfs start time plus pidfd liveness.
- A full preflight prevents malformed later entries from causing partial earlier cleanup.
- Exact inode revalidation preserves the existing pathname-replacement defense.
- The signed host lease serializes legitimate daemon startup mutation before any service is exposed.
- Legacy populated leaves remain fail closed instead of receiving unsafe guessed ownership.

### Costs and tradeoffs

- Versioned cgroup basenames are longer and Linux-specific.
- Startup must scan a bounded delegated namespace and can fail on operator-created reserved names.
- Recovery can delay startup by the configured finite quiescence bound when a stale subtree resists
  termination. The wait is event-driven rather than a millisecond wake loop.
- Empty legacy leaves are removable, but populated rev0025-era leaves require explicit operator
  remediation or a trusted migration procedure.
- The construction assumes exclusive delegated-root management. It cannot defeat root or a writer
  with equivalent mutation authority.

## Rejected alternatives

### Reclaim `_iotox_session_<pid>_<sequence>` when `/proc/<pid>` is absent

Rejected. Absence at one instant does not prove the historical owner and cannot distinguish a prior
boot or PID reuse. A populated legacy leaf remains deliberately nonrecoverable by automated startup.

### Encode only the boot ID and PID

Rejected. A PID can be reused within one boot. The creator's procfs field-22 start time is required.

### Encode only PID and start time

Rejected. Procfs start times are scoped to one boot and may repeat after restart. The canonical boot
ID is required.

### Trust the basename without pidfd acquisition and revalidation

Rejected. The process can exit or the numeric PID can change occupants while recovery is classifying
it. The pinned procfs witness, pidfd, post-open identity read, and nonblocking liveness poll form one
coherent check.

### Recover after listeners or network startup

Rejected. New sessions or a competing daemon could overlap mutation, and a service could be exposed
before its delegated namespace is known safe.

### Kill candidates while scanning

Rejected. A later malformed or unverifiable reserved entry would leave a partially mutated namespace.
The complete bounded candidate set must preflight first.

## Executable evidence

The owned registry and process oracle SHALL prove:

- strict canonical boot-ID, owner-incarnation, and session-name parsing;
- exact round trips and rejection of malformed, noncanonical, zero, overflow, and legacy-confused
  forms;
- live, exited, zombie, start-time-mismatch, boot-mismatch, and unverifiable owner classification;
- bounded recovery configuration and ordinary-filesystem rejection;
- Agent recovery after signed lease acquisition but before PTY-factory or transport activation;
- competing daemon lease refusal before any delegated-root mutation;
- live versioned-owner preservation on a real cgroup-v2 hierarchy;
- deliberate creator-crash orphan kill, recursive quiescence, and exact leaf removal;
- empty-legacy cleanup and populated-legacy refusal;
- malformed reserved-name refusal; and
- candidate-bound failure with no premature mutation.

The positive process oracle SHALL mount a fresh cgroup-v2 hierarchy inside isolated user, mount, and
cgroup namespaces. Hosts that deny those namespaces return the test's explicit skip code rather than
substituting an ordinary directory or synthetic positive result.

## Nonclaims

rev0028 does not claim:

- protection from root, a compromised daemon, or a same-UID/privileged writer that violates exclusive
  cgroup delegation;
- resource quotas, accounting policy, CPU/memory/IO isolation, or cgroup namespace confinement;
- recovery of populated PID-only legacy leaves without operator action;
- PTY/controller state continuity across daemon restart;
- power-cut durability, storage rollback resistance, or recovery from arbitrary filesystem damage;
- proof against every future kernel lifecycle race or session-escape mechanism;
- target-fleet qualification, independent security audit, or production readiness.

## Primary sources rechecked online

- Linux cgroup v2 interface and `cgroup.kill`/`cgroup.events` semantics:
  https://docs.kernel.org/admin-guide/cgroup-v2.html
- Linux `boot_id` sysctl semantics:
  https://docs.kernel.org/admin-guide/sysctl/kernel.html
- `/proc/<pid>/stat` process state and field-22 start time:
  https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
- `pidfd_open(2)` process-handle and poll semantics:
  https://man7.org/linux/man-pages/man2/pidfd_open.2.html
- `poll(2)` readiness semantics:
  https://man7.org/linux/man-pages/man2/poll.2.html

These sources define kernel interfaces. They do not audit IoTox, prove exclusive delegation, or
qualify this implementation on a production fleet.
