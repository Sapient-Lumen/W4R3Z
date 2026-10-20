# IoTox cloudtainer build report — rev0032

- **Version:** 0.32.0
- **Revision:** rev0032
- **Codename:** Exact Rational CPU Reservation Admission Citadel
- **Linked outer revision:** rev0019
- **Qualified implementation commit:** `bd5d522e65880711e002814b716f33b16036ccfa`
- **Qualified implementation tree:** `d8b71fce27f39c45bc5c55648cb4ff382a9ee2b0`

## Result

rev0032 closes the aggregate CPU admission gap left explicit in rev0031. Linux `cpu.max` is a finite
quota/period ratio rather than a raw scalar count, so IoTox now treats the administrator-selected
aggregate CPU ceiling as one exact average-bandwidth ratio and accounts every enabled session at one
explicit aggregate period. An omitted aggregate period selects 100000 microseconds. A period without a
quota, a session without a finite effective quota, a session that exceeds the aggregate ratio, and a
ratio that cannot be represented as an integral quota at the selected accounting period all fail
closed.

Exact ratio ordering reuses the continued-fraction comparator introduced for profile composition,
avoiding floating point and overflowing cross-products. Normalization divides periods by their GCD,
requires divisibility before scaling, checks multiplication, and rechecks the normalized result against
the ceiling. No hidden floor, ceiling, nearest, or stochastic rounding is accepted.

The production admission controller resolves process, memory, swap, and normalized CPU into one
canonical charge and atomically tests/adds the whole vector before helper validation, filesystem work,
PTY allocation, cgroup-leaf creation, or process spawn. Its move-only reservation token carries CPU
through move construction, move assignment, pre-spawn rollback, exact lifecycle release, and
conservative stranding. An unproved post-spawn teardown retains the complete charge and blocks later
reuse rather than undercounting uncertain work.

Agent activation validates every enabled profile before delegated-tree recovery or network activation,
and the production process factory recomputes the same charge at spawn. Owner-private runtime status
publishes whether aggregate CPU accounting is configured, its quota and period, current and peak
normalized quota totals, and the existing rejection/stranding evidence. The CLI exposes explicit
aggregate quota and period options; no Ratox packet, remote request, profile record, or peer identity
gains authority over this host policy.

## Validation summary

- GCC 14.2 Debug warnings-as-errors configure/build: pass; complete 16-route CTest surface: 15 pass,
  1 configured skip, 0 fail.
- Clang 17.0 Debug warnings-as-errors configure/build: pass; complete 16-route CTest surface: 15 pass,
  1 configured skip, 0 fail.
- GCC 14.2 Release warnings-as-errors configure/build: pass; complete 16-route CTest surface: 15 pass,
  1 configured skip, 0 fail.
- Direct GCC Debug owned registry: 337/337 checks, 0 failures.
- Clang 17 ASan+UBSan: all 16 owned-registry shards plus every process, CLI, and analyzer route;
  31 routes total, 30 pass, 1 configured skip, 0 fail, with no sanitizer diagnostic.
- GCC 14 ThreadSanitizer: all 16 owned-registry shards plus every process, CLI, and analyzer route;
  31 routes total, 30 pass, 1 configured skip, 0 fail, with no race diagnostic.
- Real-kernel cgroup lifecycle/recovery oracle: pass.
- Real-kernel cgroup resource-controller oracle: configured skip code 77 because the required `cpu`
  controller is not preactivated for child cgroups on this host. No positive controller-enforcement
  qualification is claimed.
- Product identity: `IoTox 0.32.0 rev0032`; both aggregate CPU CLI options are present.
- Implementation-commit `git diff --check`: pass; `git fsck`: pass; tracked symlink entries: 0.

Sanitizer CTest commands were split into non-overlapping route ranges only to fit the execution
wrapper's bounded command window. The retained route inventory, explicit exit files, and transcripts
cover every route exactly. Preliminary interrupted aggregate runs are not retained as positive
evidence.

## Focused proof surface

The direct registry adds one focused test family and expands from 336 to 337 named tests. Its bounded
rational lattice evaluates 1,120 aggregate/session quota-period combinations against an independent
small-integer cross-product/divisibility oracle. Additional checks cover default periods, missing
finite quota, oversized ratios, nonintegral normalization, aggregate-policy semantic bounds, scalar-
only compatibility, exact current/peak/release/strand accounting, move-only behavior, deterministic
12-thread saturation, failed-spawn rollback, factory pre-mutation rejection, Agent pre-network
rejection, CLI validation, and runtime rendering.

## Research and construction evidence

Construction rechecked Linux cgroup-v2 `cpu.max`, CFS bandwidth, and systemd delegated-tree ownership
interfaces online on 2026-08-19. The applied review is
`docs/research/exact-rational-cpu-reservation-admission-rev0032.md`; ADR 0083 freezes the exact
normalization, admission, lifecycle, authority, and observability contract. Revision-owned source
identity, transcripts, exit codes, source URLs, and checksums are under `artifacts/rev0032/`.

## Nonclaims

rev0032 accounts configured average CPU bandwidth; it does not align independent replenishment
boundaries, enforce a parent `cpu.max`, rewrite per-session periods, reserve processor time, model
burst concurrency, infer available CPUs, or guarantee latency, throughput, or later kernel allocation.
It does not implement CPU weight/burst policy, real-time/deadline policy, cpusets, aggregate I/O,
PSI-adaptive admission, a shared capacity lease across independent daemons, dynamic policy reload,
protection from root or an equivalent delegated writer, namespace/container/VM isolation, public-Tox
network qualification, target-kernel-fleet qualification, physical-host R7 qualification, independent
security audit, or production readiness.
