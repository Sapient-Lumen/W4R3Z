# Memory work, swap failure, freeze, and IRQ accounting — applied review for rev0037

Date: 2026-08-19
Scope: current Linux cgroup-v2 `memory.stat`, `memory.swap.events`, `cgroup.stat.local`, and
`irq.pressure` semantics; bounded parsing; descriptor-pinned teardown evidence; private aggregation.

## Primary sources reviewed online

1. Linux kernel documentation, **Control Group v2**

   https://docs.kernel.org/admin-guide/cgroup-v2.html
2. Linux kernel documentation, **PSI — Pressure Stall Information**

   https://docs.kernel.org/accounting/psi.html
3. Linux kernel source, **include/linux/psi_types.h**

   https://github.com/torvalds/linux/blob/master/include/linux/psi_types.h
4. Linux kernel source, **kernel/sched/psi.c**

   https://github.com/torvalds/linux/blob/master/kernel/sched/psi.c

The sources define current Linux interfaces and implementation state. They do not audit IoTox,
certify this construction host, qualify a deployment fleet, or establish production readiness.

## Applied findings

### `memory.stat` exposes stable cumulative work counters among footprint fields

The cgroup-v2 documentation defines `memory.stat` as a read-only flat-keyed non-root interface and
warns consumers to resolve fields by key because new entries can appear. It defines:

- `pgfault` as total page faults;
- `pgmajfault` as major page faults;
- `pgscan` as pages scanned on inactive LRU lists;
- `pgsteal` as pages reclaimed;
- `pswpin` as pages swapped into memory;
- `pswpout` as pages swapped out of memory.

Applied construction:

- IoTox opens one protected descriptor before payload attachment.
- `pgfault` and `pgmajfault` are the mandatory base tuple.
- `pgscan`/`pgsteal` and `pswpin`/`pswpout` are independent optional all-or-none tuples so an older or
  differently configured kernel remains distinguishable from an observed zero.
- Unknown canonical numeric fields are accepted without being retained; key order is irrelevant.
- Duplicate keys, partial tuples, signs, leading zeroes, overflow, nonnumeric values, truncation,
  blank lines, and oversized records fail closed.
- Only cumulative work counters are retained. Instantaneous footprint and implementation-detail
  fields are deliberately excluded from the completed-session aggregate.

### Swap events distinguish thresholds from allocation failure

The documentation defines `memory.swap.events` with `high`, `max`, and `fail`. `max` counts attempts
that would cross the cgroup maximum and fail; `fail` also includes system-wide swap allocation
failure. This means the fields are related but not interchangeable and do not by themselves prove a
single cause.

Applied construction:

- A configured IoTox swap ceiling requires a protected `memory.swap.events` interface; otherwise the
  interface is optional.
- All three documented fields are mandatory in an observed record and retained independently.
- A fresh leaf must begin at zero and the final absolute counters are read only after recursive
  quiescence.
- Projection names the counters as events and keeps the documented causal ambiguity. It does not
  classify `fail` as necessarily caused by the configured cgroup maximum.

### Local freeze duration is cumulative and leaf-specific

Current cgroup-v2 documentation defines `cgroup.stat.local` in non-root cgroups with cumulative
`frozen_usec`, measuring the interval from freeze initiation until thaw initiation, including freezing
imposed by an ancestor.

Applied construction:

- The interface is independently optional for kernel compatibility.
- IoTox pins and verifies it before attachment, requires a zero baseline, and retains the final
  cumulative microseconds after quiescence.
- The live private-cgroup oracle freezes and thaws an attached payload where this interface exists,
  requires positive final `frozen_usec`, and compares the exact pre-removal record with the one-shot
  outcome.
- The value is not treated as payload runtime, scheduler delay, or proof of which actor requested
  freezing.

### Current IRQ PSI has `full` but no `some` state

The cgroup-v2 documentation exposes `irq.pressure` for IRQ/SOFTIRQ pressure. Current kernel
`psi_types.h` defines `PSI_IRQ_FULL` under IRQ time accounting but no `PSI_IRQ_SOME`; current PSI source
accounts IRQ time to that state for the current task's PSI group and ancestors.

Applied construction:

- IoTox uses a dedicated IRQ pressure semantic type rather than forcing it through the resource PSI
  contract that requires `some`.
- The bounded parser requires one complete canonical `full` row with `avg10`, `avg60`, `avg300`, and
  `total`; rolling values are validated but only absolute total microseconds are retained.
- Future well-formed classes and numeric fields are grammar-checked but do not receive current
  semantics.
- Interface absence is explicit. The construction host does not expose `irq.pressure`, so parser,
  aggregation, projection, and optional-live-absence behavior are qualified without claiming a
  positive host IRQ PSI result.

### One completion decision covers the entire outcome

The existing outcome boundary reads kernel evidence only after recursive `cgroup.events:populated=0`
and before exact leaf removal. This ordering prevents live descendants from changing counters after
capture and keeps the values attached to the same descriptor/inode opened before attachment.

Applied construction:

- Every selected descriptor is included in the initial zero proof and final protected read.
- Any final read, control-state, or parse failure makes `telemetry_complete=false` for the whole
  session and suppresses all partial aggregation.
- One reservation accepts at most one outcome.
- Complete totals and capability counts use saturating arithmetic.
- Owner-private status remains unlabeled and content free.

## Implementation boundary

rev0037 implements:

- protected pre-attachment `memory.stat`, `memory.swap.events`, `cgroup.stat.local`, and
  `irq.pressure` descriptor handling with policy-linked mandatory/optional rules;
- strict bounded key-based memory, swap-event, and local-stat parsers;
- dedicated current-kernel-correct full-only IRQ PSI retention;
- exact zero fresh-leaf baselines and post-quiescence/pre-removal one-shot reads;
- whole-record and nested-tuple capability counts;
- saturation-safe page-fault, major-fault, scan, reclaim, swap-page, swap-event, freeze-microsecond,
  and IRQ-full-microsecond aggregates;
- owner-private runtime projection without identifying labels;
- direct parser, malformed-record, one-shot, saturation, projection, fuzzer, and live lifecycle
  qualification.

rev0037 does not implement:

- continuous memory/IRQ/freeze monitoring, histories, rates, percentiles, alerts, triggers, or
  adaptive policy;
- address/process/file/command/peer attribution, working-set inference, swap-byte derivation,
  interrupt-source diagnosis, or threshold-cause classification;
- persistence of completed-session aggregates across daemon restart;
- privileged-writer exclusion, target-fleet qualification, independent security audit, or production
  activation.

## Construction-host observations

The construction host runs Linux 6.18.35 with cgroup v2. Its current root exposes `memory.stat`,
`memory.swap.events`, and `cgroup.stat.local`; `irq.pressure` is absent. The private cgroup lifecycle
oracle can mount a fresh cgroup-v2 hierarchy, create a Ratox-style session leaf, attach a payload,
induce post-attachment anonymous page faults, freeze and thaw it when local freeze accounting exists,
kill it through `cgroup.kill`, prove recursive emptiness, read final kernel files, remove the exact
leaf, and compare every available value with the one-shot outcome. The controller-specific memory,
CPU-bandwidth, and I/O policy routes remain explicit code-77 skips when the outer container does not
provide writable preactivated delegation. No synthetic positive swap-failure or IRQ-pressure result is
claimed from those skips or from absent interfaces.
