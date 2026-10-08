# Rev0806 research notes

Accessed 2026-07-16. These sources inform architecture and measurement; they do
not enlarge the set of behavior claimed by rev0806.

## Build ownership: use source-owning targets, not a convenient mega-library

CMake distinguishes ordinary/static libraries from `INTERFACE` libraries. An
interface library can carry usage requirements without compiling sources or
producing a normal library artifact. CMake also defines `PUBLIC` link items as
part of both a target's own link line and its transitive link interface.

Sources:

- CMake `add_library`, “Interface Libraries”:
  https://cmake.org/cmake/help/latest/command/add_library.html#interface-libraries
- CMake `target_link_libraries`, transitive/public link interface:
  https://cmake.org/cmake/help/latest/command/target_link_libraries.html

Rev0806 therefore uses two real static source owners—one for reporting
selftests and one for the sync-domain model corpus—and one source-free interface
aggregate used only where both are intended. Merely moving both sources into a
single new static library would still make focused diagnostics inherit the
8,905-line corpus. The target graph, not the filename, determines who pays.

## Compile profiling: rank the next split from evidence

Clang's `-ftime-trace` emits Chrome-trace-compatible JSON and supports a
configurable event granularity. It is designed for identifying compilation
hotspots rather than serving as additive wall-clock accounting.

Source:

- Clang Users Manual, `-ftime-trace` and `-ftime-trace-granularity`:
  https://clang.llvm.org/docs/UsersManual.html#cmdoption-ftime-trace

Rev0806 records traces for both split units. In the runtime unit, the largest
individual parse events are concentrated in checkpoint operator status,
scheduler planning/execution, fake-peer session execution, and daemon-loop
execution. In the diagnostic unit, the single 8,700-line model function itself
is the dominant parse/optimization event. This supports two different next
moves:

1. split the production domain by invariant owner, starting with the checkpoint
   scheduler/operator/daemon cluster; and
2. split the diagnostic corpus into scenario-owned functions without turning
   test helpers into public runtime API.

## Crash proof: process and VFS cuts remain the right next oracle

SQLite documents crash and power-loss testing that runs database work in a
separate process and uses a specialized VFS to simulate reordered, incomplete,
or lost writes before checking post-crash database integrity and transactional
outcomes.

Source:

- SQLite testing documentation, power-loss crash testing:
  https://sqlite.org/testing.html#power_loss_crash_testing

AnonSync still needs a domain-level oracle above SQLite integrity: receipts,
checkpoint rows, staged bytes, sidecars, manifests, and externally visible file
publication must describe one recoverable transition. The current deterministic
corpora are valuable examples, not exhaustive crash-cut coverage.

## Convergence speculation: deltas are useful only after the algebra exists

Delta-state CRDT work describes small joinable state fragments and anti-entropy
conditions that can preserve convergence while reducing transmission compared
with full-state exchange.

Source:

- Almeida, Shoker, Baquero, “Delta State Replicated Data Types,” arXiv:1603.01529:
  https://arxiv.org/abs/1603.01529

A delta mechanism is not itself a convergence proof. AnonSync should first
classify each durable operation by commutativity, idempotence, monotonicity,
causal prerequisites, epoch compatibility, and required coordination. Only then
should it experiment with delta anti-entropy or an evidence DAG.
