# IoTox cloudtainer build report — rev0035

- **Version:** 0.35.0
- **Revision:** rev0035
- **Codename:** Pressure Stall Kernel Accounting Citadel
- **Linked outer revision:** rev0022
- **Qualified implementation commit:** `ceece567afa697a4ae6952694952c600a913df99`
- **Qualified implementation tree:** `d1ac1f49a9964ab2e064b59b55bccf5b1cf4ec8a`

## Result

rev0035 extends the delegated cgroup-v2 terminal outcome boundary with exact cumulative Linux Pressure
Stall Information (PSI) for CPU, memory, and I/O. Each newly created Ratox session leaf attempts to pin
protected read-only `cpu.pressure`, `memory.pressure`, and `io.pressure` descriptors before payload
attachment, independently of whether the corresponding resource ceiling is configured. Missing PSI
interfaces remain explicitly unavailable and do not block otherwise valid containment.

When the kernel exposes `cgroup.pressure`, IoTox also pins and reads that control. A present value must
be exactly enabled (`1\n`); a present disabled value fails interpretation rather than publishing
fabricated zero-pressure evidence. Every available pressure record must begin at an absolute zero
baseline in the fresh leaf. After recursive `populated=0`, and before exact leaf removal, IoTox reads
the same pinned descriptors and retains cumulative `some` and, where supported, `full` totals in
microseconds.

The new parser is bounded, LF-terminated, duplicate rejecting, and integer-overflow checked. It
requires the canonical `some` class, accepts an optional `full` class for compatibility with older CPU
PSI interfaces, requires `avg10`, `avg60`, `avg300`, and `total` on known classes, validates rolling
averages as canonical two-decimal percentages no greater than `100.00`, and accepts only well-formed
numeric future keys or classes. Rolling averages are validated but deliberately not retained.

Outcome retention remains one-shot and all-or-nothing. A read, control-state, or parse failure marks
the entire session outcome incomplete and contributes no partial counters. Complete outcomes
saturatingly aggregate independent observed-interface counts, observed-`full` counts, `some`
microseconds, and `full` microseconds for all three resources. Twelve content-free totals are projected
only through the owner-private runtime status surface. No path, command, peer, terminal, profile,
device, payload, or rolling sample is retained.

The terminal profile and local wire format remain canonical v5. PSI is observability, not admission or
enforcement: rev0035 adds no threshold trigger, polling loop, dynamic resource decision, or aggregate
capacity claim.

## Validation summary

- GCC 14.2 Debug warnings-as-errors build: pass.
- GCC Debug CTest: all 18 configured entries completed; 15 passed, three named capability skips, and
  zero failures.
- Direct owned-registry route: pass; the revision-owned registry contains 346 checks.
- Cgroup lifecycle/recovery process oracle: pass.
- Live memory/PID, CPU, and I/O resource routes: named skip code 77 because the construction host did
  not preactivate those controllers for child cgroups. No positive controller-enforcement result is
  inferred from those skips.
- Product identity route: pass; the binary reports `IoTox 0.35.0 rev0035`.
- Clang 17 Debug warnings-as-errors compilation and link: completed. A full CTest attempt completed
  entries 1 through 17 with 14 passes, three named capability skips, and zero failures before the
  execution window expired while starting entry 18 under severe unrelated shared-host build load.
  Entry 18, the R7 analyzer, then passed separately. This evidence does **not** claim one uninterrupted
  full Clang CTest transcript.
- Qualified implementation `git diff --check`: pass. The repository-datacube and retained-artifact
  shell scripts pass `bash -n`.
- No fresh full sanitizer, ThreadSanitizer, release, host-linked Argon2, Mutorr, stress, or complete
  libFuzzer matrix is claimed for rev0035. The terminal-cgroup fuzz target was extended in source, but
  a fresh fuzzer campaign is not represented as completed evidence.

## Focused proof surface

Parser tests freeze valid reordered CPU, memory, and I/O records; exact absolute totals; optional
`full`; accepted future numeric fields and classes; and rejection of missing mandatory fields,
duplicates, malformed spacing, unterminated records, noncanonical or overflowing integers, malformed
percentages, values above `100.00`, and nonnumeric future values. The existing terminal-cgroup fuzz
entry now offers every input to the PSI parser in addition to the PID, memory, CPU, `io.max`, and
`io.stat` grammars.

Outcome tests attach distinct CPU, memory, and I/O PSI results to complete sessions, prove one-shot
duplicate suppression, distinguish interface availability from a measured zero, distinguish `full`
availability from zero, reject partial aggregation after an incomplete outcome, and exercise
saturating counters and microsecond totals. Runtime-tree tests freeze all twelve owner-private fields.

The capability-aware lifecycle oracle reads each available pressure record from the live session leaf
immediately before removal and requires the one-shot teardown outcome to equal those exact parsed
totals. Resource-specific pressure comparisons are present in the memory, CPU, and I/O routes; on this
construction host those three routes stop with named capability skips before controller mutation.

## Research and construction evidence

Construction rechecked the official Linux PSI and cgroup-v2 documentation on 2026-08-19. The kernel
contract defines `total` as cumulative stall time in microseconds, provides per-cgroup
`cpu.pressure`, `memory.pressure`, and `io.pressure`, and documents `cgroup.pressure` as the local
accounting enable control. The applied review is
`docs/research/pressure-stall-kernel-accounting-rev0035.md`; ADR 0086 freezes capability detection,
parser grammar, zero-baseline, teardown ordering, aggregation, privacy, and nonclaim boundaries.
Revision-owned transcripts, source identities, source URLs, checksums, and limitation records are
retained under `artifacts/rev0035/`.

## Nonclaims

rev0035 does not register PSI triggers, continuously sample pressure, retain rolling averages or
per-session histories, infer workload causality, attribute stalls to a command/file/peer/terminal,
change resource admission or enforcement from PSI, estimate capacity, guarantee latency, throughput,
completion time, fairness, or service level, persist pressure outcomes across daemon restart, protect
against root or an equivalent delegated co-writer, qualify a target kernel fleet, establish a genuine
public-Tox two-peer Ratox session, complete physical-host R7 qualification, provide an independent
security audit, or establish production readiness.
