# Building IoTox rev0051

IoTox is a C++20 project whose public install surface is one executable, `iotox`. The default
cloudtainer path uses runtime-loaded exact provider doubles. The standalone path can compile pinned
c-toxcore, libsodium, and Argon2 into/alongside that one product when source downloads are available.

Run commands from the repository root unless stated otherwise.

## 1. Fast owned-code build

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
ctest --preset gcc-debug --output-on-failure
./build/gcc-debug/iotox --version
```

Expected identity:

```text
IoTox 0.51.0 rev0051
```

The official-repository suite has 62 CTest entries. The direct owned C++ registry contains 844
checks. Revision-cube packaging adds the historical lone-entrance layout check when configured with
`-DIOTOX_VALIDATE_REVISION_CUBE_LAYOUT=ON`.
Warnings are errors.

### Optional static Ratox rescue toolbox

The product install remains one `iotox` executable. A separate deployment payload supplies a static
fallback shell and tools without linking them into the product:

```sh
nix build .#iotox-rescue-toolbox
file -L result/bin/oksh result/bin/toybox
result/bin/toybox
nix build .#checks.x86_64-linux.ratox-rescue-toolbox-vm -L
```

The flake pins oksh 7.9 and Toybox 0.8.14 through a separately locked static toolchain plus exact
upstream archive hashes. The output includes 240 names and notices; `sh`/`toysh` are intentionally
absent. Its two ELFs have no interpreter, dynamic dependency, or embedded Nix-store reference. The
VM gate runs the exact package through the production baseline PTY with only the toolbox in PATH.
See `docs/ratox-rescue-toolbox.md` for profile authoring and deployment limits.

When using a Nix shell that provides `libsodium.so` outside the loader's default search path, set
`IOTOX_SODIUM_LIBRARY` to that shared object before running tests. Socket-heavy tests also accept
`IOTOX_TEST_SHORT_TMPDIR=/tmp` when the inherited temporary directory is too deep for Linux
`sockaddr_un`.

Clang is equally supported:

```sh
cmake --preset clang-debug
cmake --build --preset clang-debug --parallel 2
ctest --preset clang-debug --output-on-failure
```

## 2. R8 terminal capability and confinement gate

Canonical terminal profile v5 has three local confinement tiers, hard cgroup budgets, an optional soft memory throttle, and one exact-device I/O ceiling envelope:

```text
compatibility  common capability/credential floor without an IoTox syscall or Landlock policy
baseline       the common floor plus the default architecture- and argument-checked seccomp deny floor
strict         baseline plus fail-closed MDWE and Landlock ABI 10 mutation/network/IPC restrictions
```

All three tiers discover the running kernel capability ceiling, clear and verify ambient plus
active capability sets, set the child nondumpable, and retain `PR_SET_NO_NEW_PRIVS`. A privileged
launch must also lock the reviewed securebits and empty the complete capability bounding set or fail
before exec. `baseline` is the default for newly encoded profiles. `strict` never degrades to an older
Landlock ABI: it either installs MDWE, the ABI 10 ruleset, and seccomp, or reports the exact failed
child stage and creates no target process.

Run the native capability/confinement oracle directly:

```sh
ctest --test-dir build/gcc-debug \
  -R 'iotox\.terminal-posix-process' \
  --output-on-failure
```

The oracle proves zero effective/permitted/inheritable capabilities at final exec, baseline seccomp
filter mode and denial behavior, request-level rejection of the complete compiled terminal/console
mutation ioctl set, ordinary ioctl negative-control behavior, namespace-bearing legacy-clone denial,
clone3-to-legacy fallback, real fork/thread operation, lifecycle-property freezes, high-descriptor
closure, and pidfd-revalidated session shutdown. Baseline/strict startup requires a retained child
pidfd plus pidfd signaling and readable procfs inventory. When launched with sufficient privilege it proves an
empty bounding set plus locked securebits. Strict coverage either proves allowed in-tree mutation
together with denied
out-of-tree create/truncate/unlink, TCP/UDP bind/connect/send, pathname/abstract Unix connect, external
signals, and executable-memory gain, or proves a named fail-closed startup stage on a kernel or outer
sandbox that cannot supply the required interfaces. A fail-closed result is not evidence that strict
mode is usable on that host.

## 3. R7 attested evidence chain and bounded sanitizer shards

The default owned registry remains one process:

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
ctest --preset gcc-debug --output-on-failure
```

Exercise the complete v2 schedule/sign/seal/analyze implementation directly:

```sh
python3 tools/analyze-ratox-r7.py --self-test
python3 tools/prepare-ratox-r7.py self-test
python3 tools/analyze-ratox-r7.py evidence.sealed.tsv \
  --route-evidence route-evidence.bin \
  --bulk-evidence bulk-evidence.bin \
  --json-report report.json
```

The self-test is also the `iotox.ratox-r7-analyzer` CTest target when Python 3 is present. It constructs
and co-signs a complete 12,000-row matrix, then exercises tamper, event-order, auxiliary-digest, and
symlink rejections. A real qualification command requires the exact external route and bulk evidence
bound into the sealed run and returns 0 only when every required direct-UDP/forced-TCP load cell
satisfies ADRs 0070 and 0071. The full operator sequence and 22-field raw measurement contract are in
`docs/ratox-r7-evidence-v2.md`.

Instrumented runs use finite registry shards without changing the default contamination oracle:

```sh
cmake --preset clang-asan-ubsan
cmake --build --preset clang-asan-ubsan --parallel 2
ctest --preset clang-asan-ubsan --output-on-failure
```

For a custom build set `-DIOTOX_TEST_SHARD_COUNT=N`, where `N` is a canonical integer in `1..64`.
Values outside the range fail at configure time. Sharding changes process topology, not test
selection; every registry check belongs to exactly one shard.

The final PTY payload fixture is intentionally native. In the ASan and TSan process-oracle presets
only, the profile also omits its finite `RLIMIT_AS` because the re-executed instrumented IoTox helper
has already reserved a large shadow mapping before `main()`. GCC/Clang debug and release process
oracles continue to enforce the 512 MiB address-space cap.

## 4. Terminal profile, PTY, and default-off Ratox roles

The default CTest suite runs both the in-process policy/controller checks and an independent Linux
PTY process executable:

```sh
ctest --test-dir build/gcc-debug \
  -R 'iotox\.(unit-and-integration|terminal-posix-process)' \
  --output-on-failure
```

The PTY test invokes the built `iotox` binary only through its hidden, descriptor-authenticated child
role and executes a dedicated test payload. It checks sealed cwd/environment/window state, exact
identity where the host permits it, the complete capability floor, selected confinement tier,
terminal/namespace/lifecycle argument fences, ordinary fork/thread fallback, inventory-proved
resource/descriptor policy, retained pidfd, separate-process-group session shutdown, natural-leader
orphan cleanup, binary I/O, resize, escalation, and reap. This is local Linux
process-boundary evidence, not a remote terminal service or a complete sandbox claim.

IoTox compiles separately gated host and controller roles, both disabled by default. Host
activation remains explicit and fail-closed before toxcore starts. The process is made non-dumpable
and both `RLIMIT_CORE` values are sealed at zero before `Agent` construction:

```sh
./build/gcc-debug/iotox run \
  --state "$work/device.toxsave" \
  --runtime "$work/run" \
  --enable-ratox-terminal \
  --ratox-profile-store /absolute/owner-only/profile-store \
  --ratox-helper "$(realpath ./build/gcc-debug/iotox)"
```

The profile store must satisfy `docs/terminal-profile-v6.md`; the helper must be an absolute trusted
path. A remote OPEN still requires bilateral feature negotiation, a confirmed current session, a
proven stable principal, and exact-head authority-ledger v2 capability `interactive.terminal`.
Inherited-identity profiles must set `limit-processes=0`: Linux `RLIMIT_NPROC` is UID-wide, so IoTox
rejects a nonzero value instead of allowing an apparently healthy PTY that cannot fork on a busy
account. Configure delegated-cgroup `pids.max` for a real per-session process ceiling.

For kernel-owned PTY teardown, an administrator may additionally pass one exclusive writable
cgroup-v2 delegation:

```sh
./build/gcc-debug/iotox run \
  --state "$work/device.toxsave" \
  --runtime "$work/run" \
  --enable-ratox-terminal \
  --ratox-profile-store /absolute/owner-only/profile-store \
  --ratox-helper "$(realpath ./build/gcc-debug/iotox)" \
  --ratox-cgroup-root /sys/fs/cgroup/EXPLICIT-DELEGATED-IOTOX-SUBTREE \
  --ratox-cgroup-pids-max 64 \
  --ratox-cgroup-memory-high-bytes 402653184 \
  --ratox-cgroup-memory-max-bytes 536870912 \
  --ratox-cgroup-swap-max-bytes 0 \
  --ratox-cgroup-cpu-quota-us 50000 \
  --ratox-cgroup-cpu-period-us 100000 \
  --ratox-cgroup-io-device 8:16 \
  --ratox-cgroup-io-rbps 8388608 \
  --ratox-cgroup-io-wbps 4194304 \
  --ratox-cgroup-io-riops 2048 \
  --ratox-cgroup-io-wiops 1024 \
  --ratox-cgroup-aggregate-pids-max 128 \
  --ratox-cgroup-aggregate-memory-max-bytes 1073741824 \
  --ratox-cgroup-aggregate-swap-max-bytes 0 \
  --ratox-cgroup-aggregate-cpu-quota-us 100000 \
  --ratox-cgroup-aggregate-cpu-period-us 100000 \
  --ratox-cgroup-admission-cpu-some-avg10-bp 250 \
  --ratox-cgroup-admission-memory-full-avg10-bp 100 \
  --ratox-cgroup-admission-io-full-avg10-bp 100 \
  --ratox-cgroup-admission-hysteresis-bp 25 \
  --ratox-cgroup-admission-trigger-window-us 2000000 \
  --ratox-cgroup-admission-cpu-some-trigger-stall-us 250000 \
  --ratox-cgroup-admission-memory-full-trigger-stall-us 100000 \
  --ratox-cgroup-admission-io-full-trigger-stall-us 100000
```

The path must be normalized, absolute, non-root, backed by cgroup v2, owned by the daemon UID, and
writable for child creation and process migration. Under systemd, use an actual service or scope with
`Delegate=` and preserve the single-writer rule; do not point IoTox at an arbitrary systemd-owned
slice or service subtree. Every enabled profile must use baseline or strict confinement, an exact
non-root UID distinct from the daemon, and cleared supplementary groups. IoTox then creates one
`_iotox_session_v2_<boot-id>_<pid>_<start-time>_<sequence>` leaf, attaches the helper before sending
its manifest, uses `cgroup.kill`, waits for recursive `populated 0`, and removes the exact inode before
leader reap. On daemon startup, before the PTY factory or tox transport is activated, IoTox scans the
reserved namespace under that same descriptor-pinned delegation. A leaf owned by the exact current
boot/process incarnation is preserved; a stale versioned leaf is killed and removed after bounded
recursive-quiescence proof; an empty legacy leaf is removed; and a populated legacy or malformed
reserved leaf blocks startup because a numeric PID is not a safe ownership proof. rev0029 additionally
requires every requested controller in both `cgroup.controllers` and `cgroup.subtree_control`, applies
all configured values to an empty leaf, reads them back exactly, and only then attaches the blocked
helper. Memory and swap values are bytes and must be host-page aligned; zero swap forbids swap. A CPU
quota uses a 100,000 microsecond period unless one is supplied explicitly. I/O policy names one
canonical numeric `MAJOR:MINOR`; the device and at least one positive BPS or IOPS ceiling must be
configured together. IoTox writes a complete `io.max` record, accepts kernel key reordering during
semantic readback, and attaches no helper until the exact effective values are retained.

rev0030 treats the command-line values above as the administrator-owned host ceiling. Canonical
profile v5 may add or tighten process, memory, swap, CPU, and I/O fields; `memory.high` remains the v4
soft-throttle addition. Process, memory, and swap maxima compose by the smaller configured value. CPU
bandwidth composes by the lower exact `quota/period` ratio, with no floating point or overflowing
cross-product. I/O composition requires one matching device and independently selects the lower
configured read/write BPS and IOPS values. Any enabled profile with a nonempty effective budget
requires the delegated root. Startup creates and removes one probe leaf for every distinct `(exact
payload identity, effective budget)` pair before service exposure, and the production PTY factory
recomputes the same policy before cgroup or process work. Empty host and profile policy retains rev0028
lifecycle-only cgroups; an empty root retains rev0024 pidfd/procfs supervision. A configured failure is
never downgraded.

rev0033 retains the rev0032 bound over configured post-composition process, memory, swap, and exact CPU
bandwidth maxima held by all live production PTYs. Every configured aggregate dimension requires a
finite matching effective per-session maximum, and every enabled profile must fit once on an idle
ledger or activation fails before recovery and networking. Aggregate CPU is expressed as one quota at
an administrator-selected accounting period, defaulting to 100,000 microseconds. A session ratio is
compared exactly and normalized with GCD reduction; any ratio requiring fractional quota
microseconds at that period fails closed rather than being rounded.

The production factory atomically charges the complete process/memory/swap/CPU vector before helper-
path, filesystem, PTY, cgroup-leaf, or spawn work. Pre-spawn and proved-cleanup early returns roll back
through a move-only RAII token. A successful session retains its charge until recursive descendant
death, empty-leaf removal, and leader reap. Unproved post-spawn cleanup strands the exact complete
charge until restart recovery rather than under-accounting possible work. These values are
conservative configured-maximum accounting, not physical allocation, parent-cgroup CPU enforcement,
period synchronization, or pressure-responsive admission.

`memory.high` is a soft reclaim/throttling boundary and is not counted as another hard aggregate
reservation. Effective host/profile composition selects the lower soft value and clamps it beneath
the effective `memory.max`. After proved recursive quiescence, IoTox reads local PID and memory
events, CPU statistics, and—for I/O-configured sessions—whole-leaf `io.stat` before removing the exact
leaf. rev0035 also opens each available protected `cpu.pressure`, `memory.pressure`, and `io.pressure`
interface for every leaf, requires zero cumulative totals before attachment, and captures absolute
`some` plus optional `full` stall microseconds after quiescence. A present `cgroup.pressure` control
must report accounting enabled. The factory then contributes one complete or incomplete content-free
outcome to owner-private runtime status. Counter parsing is bounded, canonical, duplicate-rejecting,
future-key-compatible, and saturating in aggregate; PSI availability counts remain distinct from zero
stall totals, and rolling averages are not retained.

rev0036 additionally opens independently optional protected `pids.peak`, `memory.peak`, and
`memory.swap.peak` descriptors before attachment, requires zero fresh-leaf records, and retains their
exact lifetime high-water marks after quiescence. It attempts `cpu.stat` even when no CPU quota is
configured, requiring usage/user/system work fields and accepting bandwidth and burst fields only as
complete nested tuples. Private aggregates publish explicit capability counts, saturation-safe peak
sums/maxima, and CPU work/bandwidth/burst totals. Peaks are completed-session evidence, not
simultaneous demand, live sampling, working sets, or admission policy.

rev0037 additionally pins protected `memory.stat`, `memory.swap.events`, `cgroup.stat.local`, and
`irq.pressure` when those interfaces are available, making the first two mandatory when the matching
memory or swap policy is configured. It requires zero fresh-leaf fault/reclaim/swap/event/freeze/IRQ
counters and retains exact final page-fault, major-fault, complete scan/reclaim and swap-in/out tuples,
swap high/max/fail events, freeze microseconds, and current-kernel IRQ `full` PSI microseconds. Private
aggregates publish interface and tuple capability counts plus saturation-safe totals. These values are
completed-session cumulative evidence, not working-set estimates, physical swap bytes, interrupt
attribution, live monitoring, or adaptive admission.

rev0038 optionally admits new PTYs through delegated-root PSI before aggregate reservation or mutable
spawn work. Host policy supplies exact basis-point maxima for CPU `some avg10`, memory `full avg10`,
and I/O `full avg10`, plus one common hysteresis width. The controller is constructed under the signed
host lease before resource-policy probes or orphan-recovery mutation, pins the exact cgroup-v2 root and
configured pressure files, and requires `cgroup.pressure=1` both before and after each complete sample.
A metric above its maximum closes the gate; once closed, every configured metric must reach
`maximum-hysteresis` to reopen. Read, parse, or accounting failure returns local `unavailable`, latches
closed, and preserves the original typed local cause in owner-private last-sample evidence. The gate is
mutex-serialized and default off. It is recent-contention load shedding, not atomic capacity,
forecasting, threshold tuning, or existing-session preemption.

rev0039 optionally registers one kernel PSI trigger per configured resource on a separately opened
read/write descriptor and polls those descriptors with one eventfd-controlled monitor thread. The common
tracking window must be a `2000000`-microsecond multiple in `2000000..10000000`; this portable grammar
does not depend on `CAP_SYS_RESOURCE` and does not request the kernel realtime PSI polling worker. Every
stall threshold must be in `1..window` and paired with the corresponding avg10 threshold. A trip closes
the gate between admissions and holds it for at least one complete window; after the hold, only a complete
sample satisfying all lower hysteresis boundaries can reopen. Monitor or descriptor failure remains
latched unavailable.

Exercise the positive NixOS/systemd delegated-cgroup gate:

```sh
nix build .#checks.x86_64-linux.ratox-cgroup-vm -L
```

This VM boots Linux 6.6.94 with `psi=1` and runs lifecycle, memory/pids, CPU, I/O, and PSI admission
oracles in separate transient systemd services with `Delegate=yes`. It is the canonical single-kernel
positive gate for Ratox cgroup behavior. It does not replace deployment-specific `run-check`, a
target service-manager policy review, parent-cgroup tuning, or long Ratox soaks.

Exercise the positive lifecycle in a fresh cgroup-v2 namespace:

```sh
ctest --test-dir build/gcc-debug \
  -R 'iotox\.terminal-cgroup-(recovery|memory-resource|cpu-resource|io-resource)-process' \
  --output-on-failure
```

On a host that exposes a non-threaded domain with the relevant controller delegated to children,
the memory/PID route proves exact `pids.max`, `memory.high`, `memory.max`, swap, and OOM-group state,
observes `EAGAIN` plus a PID-limit event, drives anonymous-memory pressure above `memory.high`, and
retains one-shot teardown counters. When `memory.pressure` exists, the route also requires exact
pre-removal PSI equality in the returned one-shot outcome. The independent CPU route proves exact
`cpu.max`, positive `cpu.stat:nr_throttled`, retained CPU/throttle counters, recursive kill, exact
removal, and the same exact equality for available `cpu.pressure`. The I/O route discovers the device
actually charged by synchronous file writes, preflights an exact `io.max` policy for that numeric
device, performs attached write I/O, requires nonzero retained write bytes and operations after exact
teardown, and compares available `io.pressure` evidence exactly. A host that cannot construct the required namespace,
topology, or controller returns CTest skip code 77 with a named reason rather than claiming positive
evidence; one missing controller cannot hide another route.

The same build compiles one shared local seqpacket security layer. `control.sock` and
`terminal.sock` require per-record kernel credentials in both directions, optionally require kernel
pidfds, reject and close ancillary descriptor injection, and bind terminal ownership to process
lifetime. rev0027 additionally multiplexes bounded administrative pending clients and active-terminal
contenders: independent leases, global/per-process quotas, accept-refill budgets, and per-cycle decode
budgets prevent silent peers from imposing their lease/grace on unrelated ready work. Exact active/
stale/replacement inode handling remains. The direct registry includes separate-process adversarial
and silent-peer coexistence checks for all of these paths; no special build flag enables them.

An enabled host also reserves the signed Ratox incarnation lane before toxcore startup. The default is
`<savedata-parent>/ratox/incarnation.state`; an explicit owner-private path may be supplied with
`--ratox-incarnation-state`. A competing daemon fails before network advertisement and cannot advance
the record. Exercise the shipped-binary restart contract with:

```sh
ctest --test-dir build/gcc-debug -R 'iotox\.ratox-restart-fence-process' --output-on-failure
```

A controller-only Agent needs no profile store and creates no process:

```sh
./build/gcc-debug/iotox run \
  --state "$work/controller.toxsave" \
  --runtime "$work/controller-run" \
  --enable-ratox-terminal-client
```

After startup it publishes owner-private `<runtime>/terminal.sock`. The same executable can connect:

```sh
./build/gcc-debug/iotox --runtime "$work/controller-run" terminal "$PEER_PUBLIC_KEY_HEX"
./build/gcc-debug/iotox --runtime "$work/controller-run" \
  terminal-resume "$SESSION_ID_HEX" "$PEER_PUBLIC_KEY_HEX"
```

While attached, the CLI samples the exact remote Ratox attachment once per second. It warns after
three unanswered deadlines but retains the session until authoritative route/lifecycle evidence or
an explicit detach. One byte-identical PING identity is reused per attachment so normal sampling
cannot exhaust frozen-v1 exact-control replay storage.

The local plane is canonical bounded Linux `SOCK_SEQPACKET`, same-user authenticated with
`SO_PEERCRED`, and frozen by `docs/terminal-client-v1.md`. Successful activation is still only a
construction seam, not a production remote-shell or complete-sandbox claim. `run/status` reports the
role gates, bounded queue/replay/process counters, and the owner-only content-free lifecycle journal.

## 5. One-binary ratox-successor fixture

```sh
./tools/run-mock-node.sh gcc-debug
```

The fixture starts a real `iotox run` process, uses the same executable as the local client, and
crosses private SOCK_SEQPACKET control plus ordinary files/FIFOs. rev0020 retains the canonical request record:

```text
<76-HEX-COMPLETE-TOX-ADDRESS><TAB><REQUEST-MESSAGE><LF>
```

to the root `request` FIFO, observes malformed and accepted lifecycle evidence, sees the resulting
public-key peer projection, and removes it through the peer's `remove` FIFO. The fixture also retains
the session, authority, durable command, text, and finite-file paths from previous revisions.

This proves the owned process and exact consumed ABI peer. It does not prove the public Tox network.

## 6. Direct operator experiment

Create a disposable work area:

```sh
work=$(mktemp -d)
chmod 700 "$work"
./build/gcc-debug/iotox run \
  --toxcore ./build/gcc-debug/libtoxcore-iotox-mock.so \
  --state "$work/profile.toxsave" \
  --runtime "$work/run" \
  >"$work/node.log" 2>&1 &
node=$!
```

Wait for readiness and inspect the surface:

```sh
for _ in $(seq 1 100); do
  [[ -S "$work/run/control.sock" && -p "$work/run/request" ]] && break
  sleep 0.05
done
./build/gcc-debug/iotox --runtime "$work/run" status
find "$work/run" -maxdepth 3 -printf '%M %p\n' | sort
cat "$work/run/request.help"
```

Send an outgoing friend request with one complete FIFO write. The mock accepts the deterministic
address below; official c-toxcore remains authoritative for real checksum/nospam behavior:

```sh
peer=C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5C5
address=${peer}010203040206
printf '%s\t%s\n' "$address" 'hello from ordinary request' > "$work/run/request"
```

Observe separate evidence:

```sh
./build/gcc-debug/iotox --runtime "$work/run" status
cat "$work/run/friend-events"
find "$work/run/peers/$peer" -maxdepth 1 -printf '%M %f\n' | sort
```

A successful FIFO write is kernel admission only. A `request-send disposition=requested` record means
local `tox_friend_add` state accepted the request. It does not prove remote receipt or acceptance,
and it grants no IoTox authority.

Remove the temporary peer and stop:

```sh
printf '%s\n' remove > "$work/run/peers/$peer/remove"
./build/gcc-debug/iotox --runtime "$work/run" shutdown
wait "$node"
rm -rf "$work"
```

The typed local operation remains available and converges on the same Agent method:

```sh
./build/gcc-debug/iotox --runtime "$RUNTIME" transport-peer-request \
  "$TOX_ADDRESS" 'request message'
```

## 7. Complete final-source matrix

The release evidence matrix deletes its own build lanes by default, then runs:

```text
GCC Debug
GCC Release
Clang Debug
Clang ASan + UBSan
GCC TSan
focused Clang static analysis of eleven critical admission, synchronization, and update translation units
twelve Clang libFuzzer targets, 5000 units each
toxsync GCC Debug/Release, portable Release, Clang Debug, Clang ASan + UBSan, and three decoder fuzzers
GCC with linked system Argon2
Mutorr preservation build and tests
```

Invoke it with an exact retained log and exit record:

```sh
set -o pipefail
IOTOX_MATRIX_JOBS=2 \
IOTOX_FUZZ_LOG=/mnt/data/iotox-rev0043-fuzzer-smoke-final.log \
IOTOX_STATIC_ANALYZER_LOG=/mnt/data/iotox-rev0043-focused-static-analysis-final.log \
  ./tools/build-matrix.sh \
  |& tee /mnt/data/iotox-rev0043-final-matrix.log
printf '%s\n' "${PIPESTATUS[0]}" \
  > /mnt/data/iotox-rev0043-final-matrix.exit
```

A release-quality transcript contains exactly one analyzer marker and ends with exactly one final marker:

```text
focused-static-analysis=pass files=11 diagnostics=0
toxsync-source-matrix=pass
final-source-matrix=pass
```

The synchronization component gate can also be run alone. It preserves the OpenSSL/SSE2 lanes and
the dependency-minimum builtin-SHA/scalar lane without linking toxsync into the IoTox daemon:

```sh
IOTOX_MATRIX_JOBS=2 ./tools/build-toxsync-matrix.sh
```

The focused lane derives exact commands from the qualified Clang Debug compilation database, runs the
explicit deep path-sensitive engine for every selected translation unit, and fails on a nonzero analyzer
exit or any emitted diagnostic. The retained-artifact refresh rejects missing, duplicate, failed, or
concatenated marker transcripts and requires the Agent stress shard denominator to equal the current
linked test registry rather than silently accepting partial or stale evidence.

Do not reuse old build directories as final evidence. A green retained binary proves only the source
from which that binary was built.

## 8. Repeated Agent/session gate

After the matrix's `gcc-debug` lane exists:

```sh
IOTOX_AGENT_STRESS_RUNS=100 \
IOTOX_AGENT_STRESS_LOG=/mnt/data/iotox-rev0043-agent-stress-final.log \
IOTOX_AGENT_STRESS_EXIT=/mnt/data/iotox-rev0043-agent-stress-final.exit \
  ./tools/agent-session-stress.sh gcc-debug
```

The tool discovers the linked registry/shard, stages its transcript privately, validates ordered run
numbers 001–100 exactly once plus one terminal summary, and only then publishes the log. A second
concurrent invocation fails closed under an exclusive lock.

## 9. Fuzzers

The matrix builds and runs:

```text
iotox_frame_fuzzer
iotox_session_fuzzer
iotox_local_control_fuzzer
iotox_terminal_protocol_fuzzer
iotox_command_fuzzer
iotox_terminal_profile_fuzzer
iotox_terminal_cgroup_fuzzer
iotox_update_bundle_fuzzer
iotox_authority_fuzzer
iotox_ratox_frame_fuzzer
iotox_interactive_state_fuzzer
iotox_interactive_service_fuzzer
```

Standalone invocation:

```sh
IOTOX_FUZZ_RUNS=5000 IOTOX_FUZZ_JOBS=2 ./tools/fuzz-smoke.sh
```

A fuzz-enabled tree must also support a complete build, not only selected fuzzer targets:

```sh
cmake -S . -B build/clang-fuzz -G Ninja \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_BUILD_TYPE=Debug \
  -DIOTOX_BUILD_FUZZER=ON
cmake --build build/clang-fuzz --parallel 2
```

The static product archive exports the ASan/UBSan runtime link requirement to every consumer while
only dedicated fuzzer targets link the libFuzzer main. Canonical seeds are copied into build-local
corpora; source corpus directories are not mutated by a fuzzer run.

## 10. Standalone source-linked product

The standalone path downloads pinned archives, verifies SHA-256, builds static libsodium and Argon2,
adds pinned c-toxcore as a CMake subdirectory, and installs one `iotox` executable:

```sh
IOTOX_JOBS=2 ./tools/build-standalone.sh
```

The build and dependency trees are incremental by default. Use
`IOTOX_CLEAN_STANDALONE=1` when a deliberately clean rebuild is required.

Useful overrides:

```text
IOTOX_DEPS_DIR
IOTOX_DEPS_PREFIX
IOTOX_STANDALONE_BUILD_DIR
IOTOX_DIST_DIR
IOTOX_CLEAN_STANDALONE=1
IOTOX_PACKAGE_SOURCES=1
CC
CXX
```

`IOTOX_PACKAGE_SOURCES=1` requires a clean tracked worktree and adds a checksummed archive of the
exact repository commit and every pinned upstream source input to the distribution directory.

To preserve an honest attempt when this environment lacks DNS/network access:

```sh
set +e
./tools/build-standalone.sh \
  > /mnt/data/iotox-rev0043-standalone-attempt.log 2>&1
code=$?
printf '%s\n' "$code" \
  > /mnt/data/iotox-rev0043-standalone-attempt.exit
set -e
```

Failure before compilation is not provider evidence. Retain the exact limitation.

## 11. Genuine peer smoke

After a source-linked binary exists, provision or validate the private test-only identity baseline:

```sh
./tools/run-real-peer-smoke.sh --prepare-keys
```

Ordinary runs reuse copies of those Tox/device keys while creating fresh authority ledgers, command
stores, runtimes, friendship, and transfer state:

```sh
./tools/run-real-peer-smoke.sh
```

The clean-room qualification gate still generates both identity layers from scratch:

```sh
./tools/run-real-peer-smoke.sh --fresh-keys
```

Run the same lifecycle with every native UDP/discovery seam disabled and only configured TCP relays
available (reused keys remain the default):

```sh
IOTOX_REAL_PEER_TCP_ONLY=1 ./tools/run-real-peer-smoke.sh
```

The current gate exercises request/send/accept, connection, canonical HELLO, unknown-device denial,
recalled-owner proof, remote self-delegation, owner-role denial, remote controller revocation,
successor nomination, successor-signed epoch transition, exact duplicate replay, old-owner denial,
successor re-entry, text, both harmless durable commands, exact finite-file completion, bilateral
public-key removal/re-add, process reconnect, receiver-ledger replay at both epochs, fresh
delegation after each cut, and bounded host measurements. TCP-only mode proves the same lifecycle
with native UDP disabled. Controlled packet faults remain an M3 gate and must not be inferred from
a pass. Release/network qualification includes both a reused-baseline run and at least one
`--fresh-keys` run. Never point the reusable cache at a live profile or package the cache, retained
work directories, RecallRoot phrases, or identity/authority state. Redacted M4 evidence is retained
in `docs/evidence/2026-08-14-owner-reentry-delegation.md` and
`docs/evidence/2026-08-14-ownership-epoch-transition.md`.

### Four-route file laboratory

The same source-linked product can compare a constant payload over one Tox connection, four files
on that connection, two independent connections, and four independent connections:

```sh
./tools/run-four-route-lab.sh --prepare-keys
IOTOX_FOUR_ROUTE_BYTES=8388608 \
IOTOX_FOUR_ROUTE_TRIALS=3 \
  ./tools/run-four-route-lab.sh --reuse-keys

IOTOX_FOUR_ROUTE_BYTES=16777216 \
IOTOX_FOUR_ROUTE_TRIALS=3 \
IOTOX_FOUR_ROUTE_STREAM_TOTALS=8,16,32,64 \
  ./tools/run-four-route-lab.sh --reuse-keys
```

This starts eight agents and uses private test-only state. Keep the default cleanup enabled; never
point its cache at production identities. `--fresh-keys` is the from-scratch qualification mode.
`IOTOX_FOUR_ROUTE_TCP_ONLY=1` is available for a separately retained relay-only experiment. The
tool proves measured behavior of the shipped source-linked client, not a product bonding protocol
or another Tox client.

### Strict routed laboratories

The local source-linked socket gate and the two-guest strict-SOCKS route gate are:

```sh
python3 tools/run-tox-tor-smoke.py
./tools/iotox-sandwurm-lab.sh up-pair tox-tor proxy-restart
```

Verify and compact the returned Sandwurm proof with:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/lab/pairs/PAIR_ID proxy-restart
./tools/iotox-sandwurm-lab.sh export-pair \
  .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/exports/pairs/PAIR_ID proxy-restart
```

The first command requires a clean tree. The VM cell reuses copies of the private test identities,
captures both TAPs before releasing those copies, kills/restarts the exact proxy endpoint, and
requires post-recovery application traffic. Its generic numeric SOCKS forwarder is not Tor; these
commands do not prove a Tor circuit or anonymity.

Qualify a locally installed Tor daemon separately with a current public numeric Tox TCP node record:

```sh
python3 tools/run-tox-operator-tor-smoke.py \
  --node IP:TCP_PORT:64_HEX_PUBLIC_KEY \
  --output operator-tor-receipt.json
python3 tools/verify-tox-operator-tor-smoke.py \
  operator-tor-receipt.json \
  --runner tools/run-tox-operator-tor-smoke.py
```

The runner refuses a dirty tree and resolves the source-linked product. It binds the Tor
binary/version/digest and normalized configuration, then requires Tor-control and Linux process-
socket evidence for a successful public relay stream on a three-hop circuit. It terminates Tor,
waits for authoritative c-toxcore offline, holds at least ten seconds while checking for UDP/direct
fallback, restarts the same endpoint, and requires another qualifying circuit. `--node` is
repeatable; the operator must independently obtain and review current numeric records. The tool
downloads no node catalog.

With c-toxcore's numeric SOCKS destinations the Tor fixture intentionally uses `SafeSocks 0`.
`SafeSocks 1` rejects numeric destinations because Tor cannot know whether an application resolved
them; IoTox instead prevents that ambiguity at its own boundary by prohibiting hostnames and native
DNS. The accepted rev0045 receipt is
`artifacts/rev0045/tox-operator-tor-smoke.json`. It proves one actual-Tor public route and restart,
not anonymity or relay reliability. The separate Sandwurm `sync-tree-route-private-actual-tor`
sample now proves two independently keyed Tor auxiliaries become private-v2 ready in one
two-IoTox sync topology; it does not attribute the tree payload to Tor. The repeated operator sample
binds local refusal after 34 ms while c-toxcore still reports TCP and keeps the later 76.990-second
authoritative offline transition independent.

Inspect the running daemon's separate content-free observations with:

```sh
iotox --runtime /absolute/private-runtime route-health
iotox --runtime /absolute/private-runtime route-health FRIEND
iotox --runtime /absolute/private-runtime \
  --watch-ms 10000 --sample-ms 250 --failure-samples 3 --recovery-samples 2 \
  route-health-watch FRIEND
iotox --runtime /absolute/private-runtime --timeout-ms 2000 route-target-health
```

The optional friend form uses the confirmed lossless echo within the ordinary control timeout. The
local SOCKS connection has its own 250 ms bound. Neither command changes c-toxcore connection truth
or a session epoch; listener reachability alone leaves upstream state unresolved. The watch holds
independent boundary/application hysteresis only in its own process. It never installs recovery
policy in the daemon or detaches/resumes Ratox (ADR 0193).
`route-target-health` is one-shot and Tox/Tor-only. It sends a numeric SOCKS5 CONNECT solely for the
first configured TCP relay, emits no endpoint or application bytes, and leaves carrier/session truth
untouched (ADR 0194).

## 12. Provider modes

Default research/test build:

```text
runtime-loaded c-toxcore
runtime-loaded Argon2
exact shared-library doubles in tests
```

Official source-linked build:

```text
IOTOX_TOXCORE_SOURCE_DIR=<verified pinned source tree>
IOTOX_ARGON2_LIBRARY=<verified library/archive>
```

The adapter remains narrow in both modes. All calls for one `Tox*` remain serialized on the owner
thread.

## 13. Refresh retained evidence

After the matrix, standalone attempt, and stress run:

```sh
IOTOX_MATRIX_EXIT_FILE=/mnt/data/iotox-rev0043-final-matrix.exit \
IOTOX_STANDALONE_ATTEMPT_LOG=/mnt/data/iotox-rev0043-standalone-attempt.log \
IOTOX_STANDALONE_ATTEMPT_EXIT=/mnt/data/iotox-rev0043-standalone-attempt.exit \
IOTOX_FUZZ_LOG=/mnt/data/iotox-rev0043-fuzzer-smoke-final.log \
IOTOX_AGENT_STRESS_LOG=/mnt/data/iotox-rev0043-agent-stress-final.log \
IOTOX_AGENT_STRESS_EXIT=/mnt/data/iotox-rev0043-agent-stress-final.exit \
  ./tools/refresh-retained-artifacts.sh \
    /mnt/data/iotox-rev0043-final-matrix.log
```

Then verify the retained payload independently:

```sh
./artifacts/run-prebuilt-tests.sh
(cd artifacts && sha256sum -c SHA256SUMS)
```

The refresh refuses to call missing lanes green unless explicitly placed in partial-evidence mode.
A release cube should use full mode.

## 14. Package

Commit the exact verified source first, then create the standalone source-input package and repository
datacube from a clean worktree:

```sh
git diff --check
git status --short
./tools/package-source-inputs.sh
cube_timestamp=$(TZ=America/New_York date +%Y.%m.%d.%H.%M.%S)
IOTOX_DATACUBE_TIMESTAMP="$cube_timestamp" \
  ./tools/make-repository-datacube.sh /mnt/data
cube=$(find /mnt/data -maxdepth 1 -type f \
  -name "IoTox-repository-datacube-${cube_timestamp}-*.zip" -print -quit)
./tools/make-repository-datacube.sh --verify "$cube"
```

The repository datacube separates the tracked source, full Git bundle, verified standalone
materials, selected raw validation logs, and optional unchanged founding cubes. It enforces a strict
size limit, rejects unsafe paths and symlinks, scans tracked history for sensitive-looking material,
and verifies checksums plus the Git bundle. Rename or copy the verified datacube to the linked outer
basename only after this check, then verify that exact renamed file again. Follow `PACKAGE.md` for the
full archive and one-link handoff contract.
