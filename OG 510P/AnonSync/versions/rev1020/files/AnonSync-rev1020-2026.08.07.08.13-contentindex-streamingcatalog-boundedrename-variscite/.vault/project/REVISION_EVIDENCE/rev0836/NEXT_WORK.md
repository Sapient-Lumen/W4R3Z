# Next work — after rev0836

## 1. Bound destructive cleanup itself

`TestProcessTopologyOwner` now prevents post-reap numeric reuse, but its
throwing and noexcept cleanup paths still use blocking `waitpid(..., 0)` after
sending `SIGKILL`. Under normal same-UID child ownership that completes quickly;
it is not a formally bounded operation if signaling is denied or the task is
stuck in an uninterruptible kernel state. The next process-boundary revision
should model cleanup as a deadline-bearing state machine, preserve the first
error, poll exact completion, and report explicit “identity relinquished but
reap unconfirmed” evidence rather than hanging a test destructor indefinitely.
The deterministic syscall oracle is the right place to define those branches
before changing integration behavior.

## 2. Add an optional pidfd backend without weakening old-kernel behavior

On kernels that support the necessary syscalls, acquire the pidfd at spawn and
use it as exact leader identity. Only enable process-group signaling when the
runtime supports the required scope semantics. Keep the WNOWAIT backend as a
separately tested compatibility path. Differentially run the same scripted
state-machine corpus against both backends.

## 3. Separate cooperative process cleanup from hostile-worker containment

Process groups do not stop `setsid()`/`setpgid()` escape. For disposable hostile
SQLite interpretation or other untrusted helpers, evaluate a delegated cgroup
v2 subtree, resource limits, seccomp, Landlock, descriptor/environment
sanitization, and parent-enforced wall-clock termination. Report unavailable
layers explicitly rather than silently degrading the claim.

## 4. Apply the same transition-owner pattern to production boundaries

The high-value production roadmap remains:

- an executable convergence algebra for every durable operation;
- a crash-cut oracle spanning SQLite, sidecars, receipts, manifests, and
  filesystem publication;
- disposable hostile-database workers; and
- an explicit confidentiality, metadata-leakage, enrollment, rotation,
  revocation, recovery, and key-erasure design.

The process-owner work is infrastructure for trustworthy tests; it does not by
itself advance distributed convergence or privacy.

## 5. Continue reducing proof-hostile compilation units

`src/sync_domain.cpp` remains 15,257 lines and `src/sync_domain_selftests.cpp`
9,053 lines. Extract one invariant owner at a time with a focused target,
independent model/oracle, dependency guard, source audit, and before/after graph
measurement. Avoid line-count-only splitting that merely moves coupled state.
