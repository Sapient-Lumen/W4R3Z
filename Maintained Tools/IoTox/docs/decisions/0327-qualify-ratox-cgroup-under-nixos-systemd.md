# ADR 0327: Qualify Ratox cgroups under NixOS systemd

- Status: accepted and implemented
- Date: 2026-09-03

## Context

ADR 0075 through ADR 0090 built the optional Ratox delegated-cgroup path: boot/process-bound
session leaves, `cgroup.kill`, pids/memory/swap/CPU/I/O controls, exact aggregate admission,
teardown-time controller evidence, PSI admission, and continuous PSI trigger monitoring. The direct
process oracles were intentionally skip-capable because the construction host does not always expose
a writable delegated cgroup-v2 hierarchy with every controller active.

That left a concrete product gap for SSH-like daily control. We had strong parser and process
ordering evidence, but not one named Linux kernel plus service-manager environment that positively
exercised every controller-dependent Ratox cgroup route.

## Decision

Add `ratox-cgroup-vm` as a NixOS KVM flake check. The guest boots with cgroup v2, `psi=1`, and
systemd. Each oracle runs inside its own transient `systemd-run --property=Delegate=yes` service so
the test crosses a real service-manager delegation rather than a permissive host shell.

The packaged harness now includes `iotox_terminal_cgroup_recovery_process_tests`. Its worker path
execs directly into `unshare -UrCm` for the controller-positive route, allowing the transient service
cgroup to be empty before the oracle constructs a private delegated subtree. If the namespace root
exposes controllers but does not preactivate them, the oracle moves itself into a sibling anchor leaf
and enables the exact required controller set before building the production `SessionCgroup` root.

The VM gate requires all five positive process oracles:

- boot-bound cgroup orphan recovery;
- pids, `memory.high`, `memory.max`, swap, OOM-group, pids rejection, memory pressure, and exact
  teardown evidence;
- `cpu.max`, actual throttling, `cgroup.kill`, removal, CPU work, and available CPU PSI evidence;
- real block-device discovery through synchronous file I/O, exact `io.max`, nonzero retained write
  accounting, and available I/O PSI evidence;
- per-cgroup PSI admission, quiet trigger registration, disabled-accounting fail-closed behavior,
  exact reopening, and serialized concurrent admission accounting.

The `io.stat` parser now accepts the kernel's zero-accounting device forms `MAJOR:MINOR\n` and
`MAJOR:MINOR \n` as empty evidence while retaining strict rejection of duplicate devices, ambiguous
spacing, malformed keyed values, and incomplete nonempty read/write tuples.

## Consequences

The x86_64 NixOS KVM guest on Linux 6.6.94 passed all five cgroup routes under systemd delegation.
This closes the first named Ratox cgroup/PSI kernel and service-manager qualification slice and gives
daily-control Ratox a real positive resource-fencing gate.

It does not prove every Linux distribution, systemd version, kernel configuration, container manager,
physical disk controller, parent cgroup policy, root-level adversary, IRQ-pressure policy, PSI
notification latency, adaptive threshold, long-duration leak behavior, Tox route traversal, or
production activation. Additional deployment kernels and an independent operations/security review
remain product-hardening work, not a reopened wire-protocol issue.
