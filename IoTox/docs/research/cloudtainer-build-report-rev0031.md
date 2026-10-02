# IoTox cloudtainer build report — rev0031

- **Version:** 0.31.0
- **Revision:** rev0031
- **Codename:** Aggregate Cgroup Reservation Admission Citadel
- **Linked outer revision:** rev0018
- **Qualified implementation commit:** `ddc5aaaef2d730532786fbf954847124c49de15d`
- **Qualified implementation tree:** `3a463d81c8fa2ba07411425dcdbc974a64c9680f`

## Result

rev0031 closes a host-capacity admission gap above rev0030's exact per-session cgroup ceilings.
Linux permits sibling cgroup limits to be overcommitted, so independently enforced session maxima can
still multiply beyond an administrator's intended envelope. IoTox now supports host-only aggregate
process, memory, and swap reservation ceilings over each session's already-composed effective
profile budget. Aggregate CPU is deliberately excluded until a canonical exact scheduling policy is
specified.

Agent activation validates every enabled profile before orphan recovery or network activation. Each
configured aggregate dimension requires a finite matching effective per-session maximum, and every
session must fit once on an idle ledger. Production admission atomically tests and charges the whole
reservation vector before helper validation, filesystem work, PTY allocation, cgroup creation, or
process spawn. Capacity checks use subtraction rather than addition, avoiding unsigned-overflow
acceptance. A move-only RAII token carries the charge through the process lifetime and rolls back all
proved pre-spawn failures exactly.

The teardown contract is intentionally fail closed. A post-spawn charge is released only after both
direct-child reap and exact session-leaf removal are proved. If bounded best-effort cleanup cannot
prove either condition, the exact charge is stranded and the owner-private stranded counter advances;
subsequent admission cannot reuse that capacity until restart recovery re-establishes tree truth. This
prevents cleanup uncertainty from becoming silent aggregate undercounting.

Runtime status exposes configured dimensions, current and peak active reservations, current and peak
reserved process/memory/swap amounts, rejections, and stranded reservations. Zero swap remains a
meaningful configured ceiling. No Ratox packet, remote request, terminal profile record, or peer
identity gains authority to select the host aggregate policy.

## Validation summary

- GCC 14.2 Debug warnings-as-errors configure/build: pass; complete 16-route CTest surface: 15 pass,
  1 configured skip, 0 fail.
- Clang 17.0 Debug warnings-as-errors configure/build: pass; complete 16-route CTest surface: 15 pass,
  1 configured skip, 0 fail.
- GCC 14.2 Release warnings-as-errors configure/build: pass; complete 16-route CTest surface: 15 pass,
  1 configured skip, 0 fail.
- Direct GCC Debug owned registry: 336/336 checks, 0 failures.
- Clang 17 ASan+UBSan: all 16 owned-registry shards plus every process, CLI, and analyzer route;
  31 routes total, 30 pass, 1 configured skip, 0 fail.
- GCC 14 ThreadSanitizer: all 16 owned-registry shards plus every process, CLI, and analyzer route;
  31 routes total, 30 pass, 1 configured skip, 0 fail, with no race diagnostic.
- Real-kernel cgroup lifecycle/recovery oracle: pass.
- Real-kernel cgroup resource-controller oracle: configured skip code 77 because the required `cpu` controller is not preactivated for child cgroups on this host. No positive
  controller-enforcement qualification is claimed.
- Product identity: `IoTox 0.31.0 rev0031`.
- Implementation-commit `git diff --check`: pass; `git fsck`: pass; tracked symlink entries: 0.

Sanitizer CTest commands were split only to fit the execution wrapper's bounded command window. The
retained route inventory, explicit exit files, and non-overlapping transcripts cover every route.
Preliminary or superseded runs are not retained as positive evidence.

## Research and construction evidence

The construction rechecked the Linux cgroup-v2 hierarchical limit/overcommit contract, Linux PSI's
role as pressure observation rather than exact configured-max reservation, and systemd's explicit
single-manager delegation boundary on 2026-08-19. The applied review is
`docs/research/aggregate-cgroup-reservation-admission-rev0031.md`; ADR 0082 freezes admission and
teardown policy. Revision-owned transcripts, hashes, exits, and exact source identity are under
`artifacts/rev0031/`.

## Nonclaims

rev0031 reserves configured maxima conservatively; it does not preallocate physical memory, swap, or
process slots and does not prove later kernel allocation success. It does not implement aggregate CPU
scheduling, I/O-controller policy, PSI-adaptive admission, a shared capacity lease across independent
daemons, dynamic policy reload, protection from root or another privileged delegated writer,
namespace/container/VM isolation, positive resource-controller qualification on this cloudtainer,
target-kernel-fleet qualification, physical-host R7 qualification, independent security audit, or
production readiness.
