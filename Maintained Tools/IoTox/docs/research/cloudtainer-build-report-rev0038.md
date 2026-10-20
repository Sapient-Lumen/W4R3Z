# IoTox cloudtainer build report — rev0038

- **Version:** 0.38.0
- **Revision:** rev0038
- **Codename:** PSI Admission Hysteresis Load Shedding Citadel
- **Linked outer revision:** rev0025
- **Qualified implementation commit:** `ba29e2725da859530970b56a64229ca67b2bdd15`
- **Qualified implementation tree:** `ec05d3e5c8af1ed8deba5e77b308374f495dea21`

## Result

rev0038 adds one default-off host-local load-shedding boundary before creation of a new Ratox PTY.
The policy samples Pressure Stall Information from the exact delegated cgroup-v2 root and applies
independent CPU `some avg10`, memory `full avg10`, and I/O `full avg10` maxima. Administrators express
all percentages as integer basis points from 0 through 10000, with one common validated hysteresis
width. The policy remains outside terminal profiles, authority state, and the Ratox wire protocol.

The shared bounded PSI parser now retains canonical `avg10`, `avg60`, and `avg300` values exactly,
without locale or binary floating point, while preserving the existing cumulative-total projection.
Current rows require unique `avg10`, `avg60`, `avg300`, and `total` fields; malformed spacing,
noncanonical decimals, signs, leading zeroes, missing or duplicate fields/classes, percentages above
`100.00`, integer overflow, truncation, and oversized records fail closed. Future numeric fields and
classes are grammar-checked without being assigned current admission semantics.

An open gate admits values exactly equal to their configured maxima and closes only when any enabled
metric is strictly greater. Once closed, the latch reopens only when every configured metric is at or
below its own `maximum-hysteresis` boundary. Zero thresholds, zero hysteresis, and the full
`10000/10000` range are exact. A read, parse, accounting-state, or evaluator failure rejects the
request, latches the gate closed, and preserves its original typed cause in owner-private evidence;
the live operation is normalized to local `unavailable` rather than exposing a kernel parse class as
a peer protocol error.

Controller construction opens the normalized delegated cgroup-v2 root without symlinks, verifies its
daemon-owned single-writer boundary, and pins `cgroup.pressure` plus every configured PSI file by
descriptor. Each sample requires exact `cgroup.pressure=1` both before and after configured reads. A
complete startup sample validates the capability and grammar without converting current pressure into
an activation failure. Construction occurs while the signed host-incarnation lease is held and before
resource-controller preflight, orphan-recovery mutation, listener activation, or network exposure.

Every live admission runs under one controller mutex before aggregate reservation, session-cgroup
creation, PTY allocation, helper creation, or payload mutation. Rejection therefore consumes no
aggregate capacity and leaves no leaf or child process. Saturating owner-private status retains the
configured dimensions and thresholds, latch state, checks, admissions, rejections, sampling failures,
close/reopen transitions, last-sample validity, typed last failure, observation presence, and last
valid configured values. No peer, terminal, profile, command, path, device, payload, or per-session
label is attached to those host-wide values.

The canonical terminal profile remains v5 and the Ratox protocol remains unchanged. This revision
changes host admission only; the completed-session cumulative PSI accounting added earlier remains a
separate teardown observation surface.

## Validation summary

- GCC 14.2 Debug warnings-as-errors: all 19 configured CTest entries completed; 15 passed, four named
  host-capability skips, and zero failed.
- GCC 14.2 Release warnings-as-errors: all 19 configured entries completed; 15 passed, four named
  host-capability skips, and zero failed.
- Clang 17 Debug warnings-as-errors: all 19 configured entries completed; 15 passed, four named
  host-capability skips, and zero failed.
- Clang 17 ASan plus UBSan: all 34 configured sharded entries completed; 30 passed, four named
  host-capability skips, zero failed, and no sanitizer diagnostic.
- GCC 14 ThreadSanitizer: all 34 configured sharded entries completed; 30 passed, four named
  host-capability skips, zero failed, and no race diagnostic.
- Clang libFuzzer: all eleven configured targets completed 5,000 runs each, including the extended
  terminal-cgroup PSI grammar surface.
- Host-linked Argon2: all 19 configured entries completed; 15 passed, four named capability skips,
  and zero failed.
- Mutorr preservation: all 21 configured entries completed; 17 passed, four named capability skips,
  and zero failed.
- Exclusive Agent/session stress: 100/100 exact repetitions passed against discovered shard 1/356.
  Prequalification exposed a scheduler-sensitive one-second deterministic-mock packet-probe deadline
  at repetition 78. The final tree preserves exact six-reply, copy-count, and arrival-rank assertions
  while allowing five seconds for the real owner/event/control thread path; repetition 78 and the
  complete final sequence pass.
- Direct owned registry: 356 fixture-aware checks, zero failures.
- Product identity: the binary reports `IoTox 0.38.0 rev0038`.
- Source-linked standalone attempt: stopped before compilation with curl exit 6 because the construction
  container could not resolve `download.libsodium.org`; the exact attempt and exit are retained, and no
  c-toxcore/libsodium/Argon2 source-linkage result is claimed.
- Qualified source `git diff --check`: pass. Every tracked shell script passes `bash -n`; Python tool
  sources compile; `git fsck` passes; tracked symlink entries, sensitive-looking history paths, and
  tracked private-key payloads are zero.
- Retained replay copies use `strip --strip-unneeded` before checksumming. The product, direct registry,
  process fixture, provider doubles, and all eleven fuzz executables preserve their runtime and dynamic
  symbol surfaces while omitting non-runtime debug/static-symbol bulk; the post-strip 356-check prebuilt
  path and checksums pass. Unstripped build trees are not packaged or claimed as retained debug artifacts.

The four named kernel-capability routes stop with CTest skip code 77. Three require preactivated memory,
CPU, or I/O controllers delegated to child cgroups. The fourth requires the per-cgroup PSI interface
`cgroup.pressure`. None of these skips is reported as positive controller enforcement or PSI evidence.

## Focused proof surface

Parser tests freeze exact current percentages, cumulative totals, optional `full`, future numeric
fields/classes, and rejection of malformed decimal shape, signs, leading zeroes, values above 100%,
missing fields, duplicates, noncanonical spacing, truncation, oversize, and overflow. Pure evaluator
tests freeze disabled policy, strict close inequality, exact maximum equality, common hysteresis,
latched reopening, zero and full-range boundaries, transition flags, missing configured observations,
and invalid-policy defense.

CLI and profile-policy tests reject malformed/out-of-range values, detached hysteresis, hysteresis
wider than any enabled threshold, and configured pressure policy without a delegated root. Agent tests
prove controller construction and capability failure while the signed host lease is held and before
resource probes, orphan recovery, listener activation, or network start. Production-factory tests
prove malformed policy fails before cgroup filesystem access, missing roots fail at construction,
ordinary filesystems cannot masquerade as cgroup v2, immutable configuration failure, pressure
admission before aggregate reservation and spawn mutation, and unchanged accounting after rejection.
Runtime-tree tests freeze every owner-private policy, state, counter, error, presence, and last-value
field.

The dedicated kernel oracle creates a private cgroup-v2 namespace when the host supports it, pins the
real root PSI interfaces, accepts a valid sample, writes `cgroup.pressure=0`, requires two fail-closed
rejections with one close transition, restores `1`, requires exactly one reopen, executes an
8-thread-by-32-check concurrent burst with exact serialized accounting, and independently proves that
disabled accounting prevents startup. The oracle intentionally does not require delegated CPU,
memory, or I/O controllers because the per-cgroup PSI interface is a distinct capability boundary.

This Linux 6.18.35 construction host mounts cgroup v2 and its kernel configuration reports
`CONFIG_PSI=y` with `CONFIG_PSI_DEFAULT_DISABLED=y`, but the container view exposes neither
`/proc/pressure` nor `/sys/fs/cgroup/cgroup.pressure`. The PSI oracle therefore records its explicit
capability skip. No synthetic file replaces the missing kernel interface, and no positive live PSI
admission result is claimed.

## Research and construction evidence

Construction rechecked the current official Linux PSI documentation, cgroup-v2 administration guide,
and kernel PSI implementation on 2026-08-19. The kernel contract defines rolling `avg10`, `avg60`, and
`avg300` pressure percentages plus cumulative `total`; exposes CPU, memory, and I/O `some`/`full`
semantics; exposes per-cgroup PSI through controller files; and defines `cgroup.pressure` as the
non-hierarchical per-cgroup accounting switch. The source confirms fixed two-decimal percentage
formatting and the accounting switch behavior. These facts support exact parsing and capability
checks, not a universal threshold or scheduling guarantee.

The applied source review is `docs/research/linux-cgroup-psi-admission-rev0038.md`; ADR 0089 freezes
the capability, parser, descriptor, ordering, state-machine, privacy, and nonclaim boundaries.
Revision-owned transcripts, exact source identity, source references, exit records, checksums, and
prebuilt smoke evidence are retained under `artifacts/rev0038/` after artifact refresh. Runtime replay
binaries are bounded stripped copies; raw source and full execution transcripts remain authoritative.

## Nonclaims

rev0038 does not choose safe pressure thresholds for a deployment; predict future capacity; guarantee
latency, throughput, fairness, availability, or deadline success; create an atomic multi-file PSI
snapshot; continuously monitor pressure between admissions; register kernel PSI triggers; adapt
resource limits; queue or prioritize rejected sessions; attribute pressure to a peer, session,
terminal, profile, command, process, device, or workload; preserve latch state across daemon restart;
protect against root or an equivalent delegated co-writer; qualify a target kernel fleet; claim the
four skipped live controller branches; establish a genuine public-Tox two-peer Ratox session; complete
physical-host R7 qualification; provide an independent security audit; or establish production
readiness. The package does not preserve unstripped debug-symbol binaries.
