# Audit — AnonSync rev0834

## Boundary under review

Rev0833's last non-inheritance raw-fork exception was small but still expressed
one evidence-producing child as unrelated local resources: PID, process group,
stdout pipe, stderr pipe, output parser, deadline, and wait status. The audit
asked whether any failure order could block forever, leak a descriptor, leave a
zombie, or accept partial evidence as authority.

## Corrected ownership model

`SelfExecTestProcess` now carries PID and both capture descriptors as one
move-only capability. Spawn uses race-free close-on-exec pipes; only parent read
ends are nonblocking. Ordered spawn actions duplicate child write ends onto
stdout/stderr before the close-from fence. The capture wait drains both streams
concurrently, checks child exit without blocking, and uses one steady-clock
deadline plus two explicit byte budgets.

Success requires all three terminal facts: the leader is reaped, stdout reaches
EOF, and stderr reaches EOF. Every timeout, overflow, read, poll, allocation, or
wait exception kills the child process group, reaps any owned leader, closes both
descriptors, and only then propagates failure.

## Executable adversarial frontier

The runtime oracle measures the actual kernel pipe capacity and writes capacity
plus 4096 bytes to each stream. A wait-before-read or one-stream-at-a-time design
would deadlock this child. Rev0834 recovers exact bytes and exits. Independent
overflow and hang cases prove fail-closed cleanup, while `/proc/self/fd` counts
prove no parent descriptor residue across the corpus.

The owner oracle passes **31/31** checks. The allocator campaign remains **642
checks across 318 workers and 312 injected cutpoints**.

## Raw-fork result

The exact active inventory is **0 production calls** and **15 test calls across
8 translation units**. All 15 are inherited-state or process-lineage probes.
The reviewed fork-exec bridge count is now **0**, and five campaigns begin in
fresh images.

This does not make every retained inheritance probe mature. Several still use
blocking read/wait ownership and are listed as next work rather than treated as
proved.

## Structural proof

Four changed-boundary audits pass **245/245**. They bind the exact fork inventory,
CMake topology, helper protocol version, pinned-boundary ordering, blocking-child
and nonblocking-parent pipe semantics, descriptor action ordering, concurrent
drain loop, monotonic timeout, byte ceilings, EOF condition, failure cleanup,
status diagnostics, runtime over-capacity oracle, and allocator fault frontier.

## Validation

The exact parent verifies 25/25 as a ZIP and 21/21 as a directory. The source
patch replays to **207/207 active files** with zero
mismatches. GCC 14 builds every target and reaches a no-work closure. The 120-test
inventory passes in seven bounded post-closure batches. Both focused targets pass
under GCC, Clang 17 `-Werror`, and Clang 17 ASan/UBSan; sanitizer coverage is not
claimed project-wide and leak detection is not claimed.

## Claim boundary

This is test-infrastructure hardening. The owner is Linux/glibc-specific and is
not a sandbox. It does not prove hostile-child containment, parent-death
behavior, arbitrary kernel/resource failures, distributed convergence, or the
privacy properties implied by the project name.
