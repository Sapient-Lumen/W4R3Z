# IoTox cloudtainer build report — rev0033

- **Version:** 0.33.0
- **Revision:** rev0033
- **Codename:** Memory-High Kernel Outcome Telemetry Citadel
- **Linked outer revision:** rev0020
- **Qualified implementation commit:** `69c1d167ff71d0ce4747de8a67d2bc48b6266871`
- **Qualified implementation tree:** `4e0ffc7fe8ff34791321b6713fbb69dbaa9109a2`

## Result

rev0033 adds a bounded memory-throttle boundary and retains content-free kernel outcomes after an exact
terminal-session teardown. Canonical local terminal profiles advance to v4 and add optional
`cgroup-memory-high-bytes`. Host and profile values compose monotonically by the stricter maximum, and
the effective throttle is clamped beneath the effective hard `memory.max`. Values must be positive and
page aligned. V1 through v3 remain decodable; v3 migration preserves every existing hard-budget field
and invents no throttle.

A configured throttle is written to `memory.high` and read back exactly. It remains distinct from the
hard OOM boundary: `memory.high` can force reclaim and allocation throttling but does not itself invoke
the cgroup OOM killer. Any memory policy continues to set `memory.oom.group=1`, preserving the session
as one lifecycle unit if the kernel must kill for a hard-memory failure.

Each new session leaf pins read-only kernel counter descriptors before a task is attached and requires a
zero baseline. PID and memory accounting prefer `pids.events.local` and `memory.events.local`; only an
unsupported-interface result permits fallback to the hierarchical records, after IoTox has already
proved that the session leaf is childless. CPU accounting reads `cpu.stat` only when a finite CPU quota
is configured. Records are bounded to 64 KiB, LF terminated, strict canonical unsigned decimal,
duplicate-key rejecting, and future-key compatible. The older-kernel absence of
`oom_group_kill` is accepted as zero; mandatory counters remain fail closed.

Outcome capture happens only after recursive `cgroup.events populated=0`, while the exact leaf inode is
still pinned, and before removal. The result can be consumed once. Missing, replaced, unreadable, or
malformed kernel evidence yields one explicit incomplete observation rather than fabricated zero
success. Complete observations retain only aggregate counters for PID-limit hits, memory high/max/OOM
activity and kills, and CPU usage/period/throttling. No command, terminal, peer, environment, or packet
content is retained.

The existing move-only aggregate reservation token now also transports the one-shot outcome even when
aggregate capacity ceilings are disabled. Cumulative counters use saturating arithmetic. Normal exit,
startup rollback, destructor cleanup, exact release, and conservative stranding paths all attempt to
record the outcome after leaf removal and before token disposal. Owner-private runtime status projects
completed/incomplete observation counts and every retained kernel counter.

CMake now cross-checks the product version, numeric components, revision, numeric revision, and codename
against both `REVISION` and the executable identity header. Qualification exposed a stale 0.32.0/rev0032
binary stamp during this work; the configure-time identity lock now prevents that internally
inconsistent handoff from recurring.

## Validation summary

- GCC 14.2 Debug warnings-as-errors configure/build: pass; complete 17-route CTest surface: 15 pass,
  2 configured skips, 0 fail.
- Clang 17.0 Debug warnings-as-errors configure/build: pass; complete 17-route CTest surface: 15 pass,
  2 configured skips, 0 fail.
- GCC 14.2 Release warnings-as-errors configure/build: pass; complete 17-route CTest surface: 15 pass,
  2 configured skips, 0 fail.
- Direct GCC Debug owned registry: 340/340 checks, 0 failures.
- Clang 17 ASan+UBSan: all 16 owned-registry shards plus every process, CLI, and analyzer route;
  32 routes total, 30 pass, 2 configured skips, 0 fail, with no sanitizer diagnostic.
- GCC 14 ThreadSanitizer: all 16 owned-registry shards plus every process, CLI, and analyzer route;
  32 routes total, 30 pass, 2 configured skips, 0 fail, with no race diagnostic.
- Real-kernel cgroup lifecycle/recovery oracle: pass.
- Real-kernel memory/PID resource oracle: configured skip code 77 because `memory` is not preactivated
  for child cgroups on this host. No positive memory/PID controller-enforcement qualification is
  claimed for this host.
- Real-kernel CPU resource oracle: configured skip code 77 because `cpu` is not preactivated for child
  cgroups on this host. No positive CPU controller-enforcement qualification is claimed for this host.
- Product identity: `IoTox 0.33.0 rev0033`; help exposes the profile/host `memory.high` option and the
  retained aggregate CPU options.
- Qualified implementation `git diff --check`: pass; `git fsck`: pass; tracked symlink entries: 0.

Sanitizer CTest commands were split into non-overlapping route ranges only to fit the execution
wrapper's bounded command window. The retained route inventories, explicit exit files, transcripts,
and evidence audit cover every route exactly. An interrupted multi-lane wrapper is not retained as
positive evidence; each affected route was rerun independently with its own zero exit.

## Focused proof surface

The direct registry expands to 340 named checks. Focused additions cover profile-v4 canonical
roundtrip, v1/v2/v3 migration, page alignment, throttle/hard-limit ordering, cross-layer clamping,
monotone host/profile composition, CLI validation, current/future/malformed keyed-counter records,
zero-padding and duplicate rejection, optional older-kernel `oom_group_kill`, mandatory CPU fields,
one-shot outcome transport, telemetry with aggregate ceilings disabled, incomplete observations,
duplicate suppression, unsigned saturation, runtime rendering, and a canonical v4 fuzz seed.

The lifecycle process oracle remains positive. The memory/PID oracle, when its controller is delegated,
checks exact `memory.high`, hard memory, swap, and OOM-group readback; an observed PID-limit rejection;
anonymous-memory pressure above the throttle; and retained teardown counters. The separately delegated
CPU oracle checks exact `cpu.max`, creates bounded busy load, requires an observed throttle, and verifies
retained usage/throttling evidence. Splitting these routes prevents one absent controller from hiding
qualification of another.

## Research and construction evidence

Construction rechecked the Linux cgroup-v2 memory, PID, CPU-stat, local-event, controller-activation,
and delegation contracts online on 2026-08-19. The applied review is
`docs/research/memory-high-kernel-outcome-telemetry-rev0033.md`; ADR 0084 freezes the profile,
enforcement, parsing, teardown, aggregation, authority, and observability boundaries. Revision-owned
source identity, transcripts, exit codes, source URLs, and checksums are under `artifacts/rev0033/`.

## Nonclaims

`memory.high` is a throttle/reclaim boundary, not a hard allocation guarantee, reservation, or OOM
trigger. Its event count is not a duration, byte total, or proof that every allocation was delayed.
Kernel event counters describe the configured cgroup interfaces; they do not identify commands, peers,
causes, or user intent. A complete zero observation means only that the monitored counters were read
successfully and remained zero.

rev0033 does not implement memory.low/min protection, PSI-adaptive policy, swap reservation, physical
memory reservation, I/O control, CPU weight/burst/real-time/deadline policy, cpusets, aggregate
`memory.high` admission, per-command attribution, continuous counter streaming, persistence across
daemon restarts, a shared capacity lease across independent daemons, dynamic policy reload, protection
from root or an equivalent delegated writer, namespace/container/VM isolation, public-Tox network
qualification, target-kernel-fleet qualification, physical-host R7 qualification, independent security
audit, or production readiness.
