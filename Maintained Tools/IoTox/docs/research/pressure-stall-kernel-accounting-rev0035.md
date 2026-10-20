# Pressure-stall kernel accounting — applied review for rev0035

Date: 2026-08-19
Scope: Linux cgroup v2 PSI interfaces, record grammar, cumulative semantics, capability handling, and
IoTox teardown-time outcome projection.

## Primary sources reviewed online

1. Linux kernel documentation, **PSI — Pressure Stall Information**

   https://docs.kernel.org/accounting/psi.html
2. Linux kernel documentation, **Control Group v2**

   https://docs.kernel.org/admin-guide/cgroup-v2.html

The sources define the kernel interfaces. They do not audit IoTox or certify a deployment.

## Applied findings

### Per-cgroup PSI uses the same nested-key record shape

The kernel PSI documentation shows resource records with `some` and `full` lines, three percentage
averages, and a cumulative `total`. With cgroup v2 mounted, each cgroup directory exposes
`cpu.pressure`, `memory.pressure`, and `io.pressure` using the same format.

Applied construction:

- IoTox adds a dedicated bounded parser rather than reusing flat counter or `io.stat` grammars.
- `some` is mandatory; `full` is optional so capability absence is not converted to zero.
- Known lines require `avg10`, `avg60`, `avg300`, and `total` exactly once.
- Key order is irrelevant, but spacing, decimal, uniqueness, LF termination, and byte bounds are
  strict.
- Well-formed future numeric keys/classes are accepted without granting them current meaning.

### Absolute totals are microseconds; averages are percentages over windows

The PSI documentation defines `avg10`, `avg60`, and `avg300` as recent percentage trends and `total`
as absolute cumulative stall time in microseconds. `some` means at least some tasks are stalled;
`full` means all non-idle tasks are simultaneously stalled. `full` is therefore not an independent
additional duration to add to `some`.

Applied construction:

- IoTox validates the averages but retains only `total` microseconds.
- CPU, memory, and I/O `some` and `full` totals stay separate.
- Fresh session leaves must report zero totals before attachment. The final absolute total is then the
  exact lifetime total for that leaf without subtraction.
- Aggregate addition saturates instead of wrapping.

### CPU `full` compatibility needs explicit absence

The PSI documentation notes historical CPU `full` compatibility behavior. Kernel and deployment
variation means a current parser must not assume every pressure record has both classes.

Applied construction:

- `CgroupPressure::full_total_microseconds` is optional.
- Aggregate status carries both resource-availability counts and full-class-availability counts.
- A present zero and an absent metric remain distinguishable.

### Per-cgroup PSI accounting can be disabled locally

The cgroup-v2 documentation defines `cgroup.pressure` as a non-hierarchical `0`/`1` control, defaulting
to `1`. Disabling it affects that cgroup's PSI accounting independently of descendants.

Applied construction:

- IoTox opens `cgroup.pressure` when the kernel exposes it.
- A present record must be exactly `1\n` at initial and final observation.
- Disabled accounting makes the outcome observation unavailable rather than producing fabricated
  zero totals.
- Absence remains compatible with kernels predating the control interface.

### PSI is observation, not an enforcement or reservation primitive

The PSI documentation describes realtime monitoring and threshold triggers that can support external
load shedding or migration. Those mechanisms require policy choices beyond the meaning of the raw
counters.

Applied construction:

- rev0035 does not write PSI triggers, poll pressure FDs, retain rolling averages, or modify session
  admission from PSI.
- PSI files are optional observability for every session leaf, independent of which cgroup resource
  ceilings are configured.
- Status is cumulative and content-free. It does not claim causality between a configured limit and a
  stall, nor identify a task, command, path, peer, profile, or block device.

## Implementation boundary

rev0035 implements:

- `CgroupPressure` with absolute `some` and optional `full` totals;
- a bounded strict/future-compatible PSI parser;
- protected optional `cgroup.pressure`, `cpu.pressure`, `memory.pressure`, and `io.pressure`
  descriptors opened before attachment;
- exact zero-baseline validation;
- post-quiescence/pre-removal one-shot capture;
- complete-or-incomplete outcome semantics with no partial aggregation;
- independent saturating CPU, memory, and I/O totals plus capability counts;
- owner-private runtime status projection;
- unit, fuzz, aggregate saturation, runtime projection, and capability-aware live-oracle coverage.

rev0035 does not implement:

- live PSI sampling, threshold triggers, alerts, or admission feedback;
- causal diagnosis, per-session histories, labels, rates, histograms, or averages;
- resource-capacity estimation, aggregate I/O admission, synchronized CPU periods, or parent CPU
  enforcement;
- privileged-writer exclusion, namespace/container isolation, fleet qualification, or production
  activation.

## Construction-host evidence

The owned registry exercises PSI grammar, absence semantics, aggregation, saturation, and runtime
projection without requiring privileged cgroup mutation. The lifecycle cgroup process oracle ran on
the construction host. The memory, CPU, and I/O resource routes remained named skips because the
host did not expose the required writable/preactivated controller delegation. No synthetic positive
pressure result is claimed. On a suitable delegated host, those routes now compare each available
pressure record read immediately before removal with the exact one-shot outcome retained after
removal.
