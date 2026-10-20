# IoTox cloudtainer build report — rev0029

**Version:** 0.29.0
**Revision:** rev0029
**Codename:** Controller-Enforced Cgroup Resource Budget Citadel
**Linked outer revision:** rev0016
**Qualified source commit:** 0451f8fbe53d8f8235ce4fed1226bfe46abc3e23

## Result

rev0029 adds an optional kernel-enforced resource envelope to the existing boot-bound delegated-cgroup
PTY lifecycle. A single host-owned policy can set `pids.max`, `memory.max`, `memory.swap.max`,
`memory.oom.group=1`, and `cpu.max`. Every requested controller must be available and active at the
delegated root, every value is applied and read back before the blocked helper is attached, and any
mismatch fails closed.

Agent startup validates policy before transport work, acquires the signed host-incarnation lease,
performs a disposable exact-identity preflight for every distinct enabled terminal identity, and only
then recovers rev0028 crash orphans. A policy without an explicit root, an inactive/missing controller,
an unsafe control boundary, an invalid value, a non-domain topology, or a probe leaf that cannot be
removed keeps Ratox offline.

## Validation summary

- GCC 14.2 Debug warnings-as-errors build: pass.
- Clang 17.0 Debug warnings-as-errors build: pass.
- GCC 14.2 Release warnings-as-errors build: pass.
- Complete direct owned registry: 330/330.
- Native and sanitizer CTest suites: GCC Debug, Clang Debug, and GCC Release each completed
  16/16 routes (14 passed, 2 topology skips, 0 failed); Clang ASan+UBSan completed 31/31
  sharded routes (29 passed, 2 topology skips, 0 failed).
- Dedicated cgroup lifecycle/recovery and resource process oracles: each returned configured
  skip code 77 because the fresh namespace root reported `domain threaded`; positive branches
  remain executable and no host qualification is claimed.
- CLI, Agent, production-factory, parser, and negative controller-policy checks: pass.
- `git diff --check`: pass at the clean qualified source commit.
- Product identity: `IoTox 0.29.0 rev0029`.

The resource-oracle executable contains positive real-kernel branches for `pids.max` fork refusal,
`cpu.max` throttling, exact memory/swap/OOM control state, recursive kill, empty proof, and removal.
On this cloudtainer the fresh cgroup namespace root reports `domain threaded`; because the production
lifecycle contract requires literal `domain` leaves and `cgroup.kill`, both namespace-backed routes
return configured skip code 77 with mode-specific reasons. No positive cgroup lifecycle or controller-
enforcement qualification is claimed for this host.

## Research and construction evidence

The implementation follows the Linux cgroup-v2, CFS-bandwidth, and systemd delegation contracts
rechecked on 2026-08-18. The applied review is
`docs/research/controller-enforced-cgroup-resource-budgets-rev0029.md`; ADR 0080 freezes the policy.
Revision-owned transcripts and machine-readable scope are under `artifacts/rev0029/`.

## Nonclaims

rev0029 does not claim I/O controller policy, adaptive PSI policy, per-profile/session-varying limits,
aggregate host-wide admission accounting, protection from root or an equivalent delegated writer,
namespace/container/VM isolation, positive resource-controller qualification on this cloudtainer,
target-kernel-fleet qualification, physical-host R7 qualification, independent audit, or production
readiness.
