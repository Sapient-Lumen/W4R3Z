# I/O bandwidth and kernel accounting — applied research for rev0034

Research date: 2026-08-19
Implementation target: IoTox rev0034
Scope: Linux cgroup v2 `io.max`, `io.stat`, nested-key parsing, cgroup writeback attribution, and
delegated-subtree ownership

## Primary sources

1. Linux kernel, **Control Group v2**
   https://docs.kernel.org/admin-guide/cgroup-v2.html
2. systemd, **Control Group APIs and Delegation**
   https://systemd.io/CGROUP_DELEGATION/

Both sources were retrieved online during rev0034 construction. The kernel documentation defines the
controller interface and accounting semantics. The systemd documentation supplies the deployment
boundary for an exclusively managed delegated subtree.

## Source findings applied

### `io.max` is per-device BPS/IOPS limiting

The kernel documents `io.max` as a read-write nested-keyed file on non-root cgroups. Lines are keyed by
numeric major/minor device identity and are not ordered. Standard keys are `rbps`, `wbps`, `riops`,
and `wiops`. Writes may contain any subset in any order; `max` removes one limit. Reads report the
standard fields, using `max` for an unbounded dimension. Duplicate keys in one write have undefined
outcome. BPS and IOPS are directional; I/O is delayed when a limit is reached, while temporary bursts
are allowed.

Applied consequence:

- IoTox policy names one canonical numeric `MAJOR:MINOR`, never a path or alias.
- It writes one complete line with all four standard keys, explicitly spelling absent dimensions as
  `max`.
- Readback is parsed semantically rather than compared by bytes or field order.
- Duplicate device/key records, missing standard fields, zero finite standard ceilings, malformed
  grammar, and noncanonical integers fail closed.
- Documentation calls the feature a rate ceiling, not a latency or deterministic-throughput
  guarantee.

### cgroup nested-key files require order-independent bounded parsing

The cgroup-v2 interface convention defines nested-key records as one top-level key followed by
space-separated `SUBKEY=VALUE` pairs. For nested-key files, subkeys may be specified in any order and
need not all be written in one operation. Interface files may gain fields.

Applied consequence:

- `io.max` and `io.stat` receive dedicated bounded LF-terminated parsers rather than reuse of the
  flat-key parser.
- Device lines and nested keys are unordered.
- Duplicate top-level devices and duplicate subkeys are rejected even though IoTox itself never emits
  them.
- Unknown future keys are accepted only when they preserve the documented key/value grammar.
- IoTox's complete `io.max` write and fresh-leaf readback require all four standard keys, removing any
  dependency on omitted-field update semantics.

### `io.stat` is per-device cumulative accounting

The kernel documents `io.stat` as a read-only nested-keyed file. Lines are keyed by major/minor device
numbers and are not ordered. Defined counters are bytes and operations for reads, writes, and discards:
`rbytes`, `wbytes`, `rios`, `wios`, `dbytes`, and `dios`.

Applied consequence:

- IoTox opens `io.stat` through the same protected controller-file boundary used by the other session
  outcomes.
- A fresh leaf must have zero known counters before helper attachment.
- Every nonempty line requires the stable read/write byte and operation counters. Discard counters are
  accepted when present and default to zero for compatibility.
- Teardown sums all device lines with saturating arithmetic after recursive quiescence and before exact
  inode removal.
- Runtime status exposes only six cumulative unlabeled totals. It does not retain device, profile,
  process, command, path, peer, or terminal content.

### Limits are overcommittable, not reservations

The cgroup-v2 resource model describes `io.max` as a limit and notes that child limits may be
overcommitted. Limits restrict consumption but do not allocate exclusive physical capacity in
advance.

Applied consequence:

rev0034 does not add I/O to the existing aggregate process/memory/swap/CPU reservation ledger. Summing
configured `io.max` rates would create a false capacity statement without a reviewed device topology,
parent capacity, scheduler model, or cross-daemon lease.

### Writeback attribution depends on filesystem and inode ownership

The kernel explains that cgroup writeback combines the memory and I/O controllers. Dirty pages are
tracked per page, while writeback attribution is tracked per inode. An inode is assigned to a cgroup;
all writeback for its dirty pages is attributed to that cgroup. Ownership can move when different
cgroups write the same inode, and filesystems without cgroup writeback support attribute writeback to
the root cgroup.

Applied consequence:

- IoTox does not claim that a configured device captures every byte a process logically writes.
- The live oracle creates a fresh file after the writer is attached and uses synchronous completion,
  then requires actual `io.stat` evidence before qualifying the host route.
- Shared-file workloads, layered filesystems, and unsupported writeback paths require target-specific
  qualification.
- Whole-leaf totals are retained without causal file or command labels.

### Delegation is a single-writer contract

The kernel's top-down controller rules require `io` to be available and activated by the parent before
a child may use it. systemd's delegation guidance assigns a subtree to one manager rather than
allowing competing writers to mutate the same controls.

Applied consequence:

- IoTox requires `io` in both `cgroup.controllers` and `cgroup.subtree_control` for the delegated root.
- It retains descriptor-relative no-follow traversal, ownership/mode/type checks, payload
  non-writability, exact inode pinning, and startup preflight.
- An unexpected extra `io.max` device line in a fresh session leaf is refused rather than normalized
  away.
- Privileged or same-authority competing writers are outside the proved boundary and remain an
  explicit nonclaim.

## Construction result

rev0034 turns the research into:

- canonical profile v5 and host CLI parity for one exact device plus four directional ceilings;
- strict device/rate validation and monotone host/profile composition with device mismatch refusal;
- delegated `io` activation, complete `io.max` writes, semantic readback, and blocked-helper ordering;
- bounded future-compatible nested-key parsers for `io.max` and `io.stat`;
- protected zero-baseline I/O accounting and one-shot teardown capture;
- saturating read/write/discard bytes and operations in factory and private runtime truth;
- profile migration, CLI, parser, overflow, aggregation, projection, and capability-aware live-kernel
  regression coverage.

The construction environment exposed `io` and a genuine root `io.stat` line but did not preactivate
`io` for delegated children. The new process oracle therefore returned named skip code 77. It did not
fabricate a positive enforcement result. On a suitable target the same route discovers a device from
a synchronous-write probe, verifies semantic `io.max` policy, performs session I/O, and requires
nonzero teardown counters.

## Limits retained

This work does not discover storage topology, provide stable device naming, support multiple policy
devices, reserve aggregate physical bandwidth, guarantee latency or queue depth, apply I/O weights or
cost models, diagnose files or commands, sample rates continuously, adapt from PSI, protect against a
privileged co-writer, qualify a deployment fleet, or establish production readiness.
