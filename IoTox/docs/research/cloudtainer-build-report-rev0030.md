# IoTox cloudtainer build report — rev0030

- **Version:** 0.30.0
- **Revision:** rev0030
- **Codename:** Profile-Scoped Cgroup Budget Ceiling Citadel
- **Linked outer revision:** rev0017
- **Qualified implementation commit:** `10e05567a7fd54011102a6b3d9daaa00a76f59d6`
- **Qualified implementation tree:** `e6f3403d6c0ab8fcaef9081097495ef281662087`

## Result

rev0030 advances the optional delegated-cgroup PTY boundary from one host-global resource envelope to
profile-scoped process, memory, swap, and CPU budgets beneath an administrator-owned ceiling. The
canonical local encoder emits `iotox-terminal-profile-v3`; canonical v1 and v2 records remain readable
and migrate with an empty profile budget. Ratox wire bytes, authority, and remote request syntax do not
select limits.

Host and profile limits are validated independently and composed monotonically. Process, memory, and
swap maxima select the smaller configured value; zero swap remains a meaningful strict value. CPU
bandwidth selects the lower exact quota/period rational, with an omitted period interpreted as 100,000
microseconds. The comparison uses continued fractions, avoiding floating-point drift and overflowing
64-bit cross-products. Equal ratios retain the host representation.

Agent activation computes every enabled profile's effective policy after the signed host-incarnation
lease and before orphan recovery or network activation. Disposable controller probes are deduplicated
by `(payload identity, effective budget)`, so one identity with different profile limits receives
distinct proof. The production POSIX factory independently recomputes composition before filesystem or
spawn work. Any effective budget without an explicit delegated root fails closed.

## Validation summary

- GCC 14.2 Debug warnings-as-errors configure and build: pass.
- Clang 17.0 Debug warnings-as-errors configure and build: pass.
- Direct GCC owned registry: 332/332 checks, 0 failures.
- Default CTest surface, executed in bounded groups: GCC Debug and Clang Debug each covered all 16
  routes with 15 passed, 1 configured skip, and 0 failed.
- Real-kernel cgroup lifecycle/recovery oracle: pass.
- Real-kernel cgroup resource-controller oracle: configured skip code 77 because the required `cpu`
  controller is not preactivated for child cgroups on this host. No positive controller-enforcement
  qualification is claimed.
- Terminal-profile libFuzzer lane under ASan+UBSan: 20,000 runs completed from v1, v2, v3, binding,
  and empty seeds with no final crash or sanitizer diagnostic.
- Construction defect found and repaired: the prior fuzz oracle incorrectly required v1/v2 input to
  retain the same byte length after the public encoder migrated it to v3. The final oracle checks
  semantic migration and canonical v3 idempotence instead.
- Product identity: `IoTox 0.30.0 rev0030`.
- Implementation-commit `git diff --check`: pass; tracked symlink entries: 0.

The CTest commands were split only to fit the execution wrapper's bounded command window; the retained
route inventory and transcripts cover every default route. The resource-process executable retains
positive pids, memory, swap, OOM-group, CPU-throttling, exact-readback, recursive-kill, and cleanup
branches for a suitably delegated host.

## Research and construction evidence

The implementation follows the Linux cgroup-v2 hierarchical restriction contract and systemd's
explicit delegation/single-writer contract, rechecked on 2026-08-18. The applied review is
`docs/research/profile-scoped-cgroup-budget-ceilings-rev0030.md`; ADR 0081 freezes the policy.
Revision-owned transcripts and exact source identity are under `artifacts/rev0030/`.

## Nonclaims

rev0030 does not claim I/O-controller policy, PSI-based or aggregate host admission, dynamic profile
reload, protection from root or another privileged delegated writer, namespace/container/VM
isolation, positive resource-controller qualification on this cloudtainer, target-kernel-fleet
qualification, physical-host R7 qualification, a full Release/sanitizer matrix for this revision,
independent security audit, or production readiness.
