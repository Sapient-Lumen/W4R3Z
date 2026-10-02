# IoTox local terminal profile v4

> Historical compatibility contract. The encoder emits canonical profile v7; canonical v4 records
> remain accepted and decode with no I/O policy, account groups, privilege grant, or payload pins.
> See `terminal-profile-v7.md` for the current contract.

Status: canonical in rev0033; adds a profile-scoped `memory.high` throttle to the cgroup-v2 budget composed beneath the
rev0029 host ceiling, while retaining the confinement, lifecycle, IPC, admission, and recovery
hardening accumulated through rev0022..rev0029 behind the explicit default-off Ratox host gate
Wire effect: none; terminal profiles remain operator-owned local policy and are never selected by
remote bytes
Supersedes: v4 is the canonical encoder format; canonical v1, v2, and v3 remain accepted. V1 maps to
explicit `compatibility` confinement, v1/v2 map to an empty profile cgroup budget, and v3 maps to a
budget without `memory.high`

## Purpose

A terminal profile freezes every local process-selection input for one authorized Ratox OPEN:
executable, arguments, working directory, environment, terminal type, window policy, identity,
resource limits, profile-scoped cgroup budget, shutdown timing, and kernel confinement tier. A remote peer can request terminal
operation only through a preconfigured stable-principal binding. It cannot supply shell text, argv,
paths, environment, identity, limits, or the confinement tier.

The host role remains disabled unless the operator explicitly enables it and supplies a secure profile
store and reviewed IoTox helper. Bilateral Ratox negotiation, a transcript-confirmed current online
epoch, authenticated stable principal, and exact current `interactive.terminal` authority are all
required before profile resolution.

## Store and canonical byte contract

The owner-private no-follow tree, file ownership/mode/link/type checks, profile and binding bounds, and
atomic registry replacement contract are unchanged from v1. See `terminal-profile-v1.md` for the full
filesystem layout and binding grammar.

The canonical v4 profile record has exactly one LF-terminated line per field, exact field order, no
unknown or duplicate singleton fields, lowercase even-length hexadecimal, canonical unsigned decimal,
and byte-for-byte decode/re-encode equality. Arguments, cwd, and environment values remain
hex-encoded.

## Profile record grammar

```text
iotox-terminal-profile-v4
id=<profile-id>
enabled=<0|1>
argument-hex=<hex bytes>                 repeated 1..32 times
working-directory-hex=<hex bytes>
terminal-type=<token>
inherit-environment=<name>               repeated 0..64 times, sorted
environment-hex=<name>:<hex value>       repeated 0..64 times, sorted by name
identity=inherit
    OR
identity=exact:<uid>:<gid>:1
confinement=compatibility|baseline|strict
cgroup-pids-max=none|<u64>
cgroup-memory-high-bytes=none|<u64>
cgroup-memory-max-bytes=none|<u64>
cgroup-swap-max-bytes=none|<u64>
cgroup-cpu-quota-us=none|<u64>
cgroup-cpu-period-us=none|<u64>
minimum-dimensions=<columns>:<rows>
initial-dimensions=<columns>:<rows>
maximum-dimensions=<columns>:<rows>
allow-resize=<0|1>
limit-cpu-seconds=<u64>
limit-address-space-bytes=<u64>
limit-file-size-bytes=<u64>
limit-open-files=<u64>
limit-processes=<u64>
hangup-grace-ms=<u64>
terminate-grace-ms=<u64>
kill-reap-grace-ms=<u64>
```

Example:

```text
iotox-terminal-profile-v4
id=maintenance-shell
enabled=1
argument-hex=2f62696e2f6563686f
argument-hex=666978656420617267756d656e74
working-directory-hex=2f7661722f6c69622f696f746f782f776f726b
terminal-type=xterm-256color
inherit-environment=LANG
inherit-environment=TZ
environment-hex=ALPHA:6669727374
identity=exact:65534:65534:1
confinement=strict
cgroup-pids-max=8
cgroup-memory-high-bytes=67108864
cgroup-memory-max-bytes=134217728
cgroup-swap-max-bytes=0
cgroup-cpu-quota-us=25000
cgroup-cpu-period-us=100000
minimum-dimensions=20:5
initial-dimensions=100:30
maximum-dimensions=240:80
allow-resize=1
limit-cpu-seconds=10
limit-address-space-bytes=134217728
limit-file-size-bytes=1048576
limit-open-files=32
limit-processes=8
hangup-grace-ms=20
terminate-grace-ms=40
kill-reap-grace-ms=60
```

All v1 bounds and grammars for IDs, arguments, normalized absolute paths, terminal type, inherited and
fixed environment, identity, dimensions, limits, and graces remain in force.

## Compatibility migration

The decoder accepts all four exact headers:

```text
iotox-terminal-profile-v1
iotox-terminal-profile-v2
iotox-terminal-profile-v3
iotox-terminal-profile-v4
```

A canonical v1 record has neither confinement nor cgroup-budget fields and decodes as
`confinement=compatibility` with an empty `cgroup_limits` value. A canonical v2 record carries the
confinement field but no cgroup-budget fields and also decodes with an empty `cgroup_limits` value. A
canonical v3 record carries the five original cgroup-budget fields and decodes with absent
`maximum_memory_high_bytes`. Each input is checked against its own version-specific canonical encoder,
so malformed hybrids, unknown fields, reordered fields, noncanonical decimals, and alternate
spellings of `none` are rejected. The public encoder always emits v4. Re-encoding v1, v2, or v3
therefore performs an explicit, reviewable migration without inventing a soft memory throttle.

New C++ `Profile` values default to `baseline` confinement and an empty profile cgroup budget.

## Common native child floor

All three modes receive the existing PTY/session/process-group, controlling-terminal, foreground,
window, signal-reset, rlimit, core-disablement, exact environment, identity, parent-death, startup,
shutdown, descriptor, and `umask(077)` contracts. rev0022 adds the following common floor:

- helper setup is nondumpable before and after credential work;
- `PR_SET_NO_NEW_PRIVS=1` is set and verified;
- the runtime capability ceiling is discovered and bounded;
- ambient capabilities are cleared and read back across that ceiling;
- effective, permitted, and inheritable capability sets are cleared and read back before exec;
- privileged launches must lock root/set-ID/keep-caps/ambient securebits and empty the bounding set;
- a privileged context that cannot establish the required seal fails before target execution.

The final target may become dumpable again because ordinary exec resets that property. The other
capability, securebits, `no_new_privs`, and confinement properties persist.

rev0023 additionally makes descriptor closure independent of `RLIMIT_NOFILE`: `close_range(2)` is
followed by a two-pass `/proc/self/fd` inventory that closes and then proves every unreserved descriptor
absent. All modes fail before exec if that postcondition cannot be established.

Baseline and strict require working `pidfd_open(2)`, `pidfd_send_signal(2)`, and a readable inventory
verified as procfs before PTY allocation, then require a retained close-on-exec leader pidfd after
spawn. Exit observation prefers `waitid(P_PIDFD, ..., WNOWAIT)` with a narrow direct-child wait
fallback. Shutdown opens each numeric member directory relative to the pinned procfs inventory,
parses PID/session/live-state/field-22 start time, pidfd-opens the numeric PID, and re-reads the same
witnesses through the pinned directory before signaling. Once SIGKILL begins, three consecutive full
inventories with no live executable member are required before the waitable leader is reaped; any
member resets the count. Natural leader exit uses the same cleanup while preserving the leader's
status. Compatibility retains the historical process-group lifecycle.

## Optional delegated cgroup-v2 lifecycle

The host option `--ratox-cgroup-root PATH` is independent of the profile record and is empty by
default. When configured, Agent activation requires the production POSIX factory, baseline or strict
profiles only, and an exact non-root uid distinct from the daemon with supplementary groups cleared.
The root must be a normalized non-root absolute path reached component-by-component without symlinks,
backed by cgroup v2, owned by the daemon uid, not writable by group/other or by the payload identity,
and writable by the supervisor at the process-migration boundary.

For every PTY spawn the supervisor creates one
`_iotox_session_v2_<boot-id>_<pid>_<start-time>_<sequence>` leaf. The name canonically binds the leaf
to the daemon's current Linux boot identity, numeric PID, and procfs field-22 start time. The
supervisor immediately pins its device and inode, verifies the leaf and required control files remain
supervisor-owned, requires a plain empty domain with no enabled child controllers, and opens all
lifecycle interfaces close-on-exec. The spawn helper remains blocked waiting for its manifest while
the parent moves it into the leaf and proves it is the exclusive initial member. Only then can the
helper execute credential, confinement, and target setup.

Explicit final KILL and natural-leader cleanup write `1` to `cgroup.kill`. The supervisor waits on
kernel `cgroup.events` notifications until the leaf's recursive `populated` field becomes zero, removes
only the exact pinned leaf, and only then reaps the waitable leader. Earlier HUP and TERM grace stages retain the reviewed
pidfd/procfs session signaling path. Missing controls, read-only delegation, ownership mismatch,
identity mismatch, malformed kernel records, unexpected population, or inode replacement fail closed;
there is no downgrade to procfs-only lifecycle when the option was requested.

Before any configured PTY factory or transport service is activated, the daemon holds the durable
device-bound Ratox host-incarnation lease. It first creates and removes one exact-identity probe leaf
for each distinct enabled payload identity; only after every probe succeeds does it scan a bounded
reserved-name set under the pinned delegation. Every candidate is fully opened and validated before
mutation. A versioned leaf is
preserved only when the current boot ID, pidfd lifetime, procfs PID, start time, and nonterminal task
state all match. A proven-stale leaf receives the same recursive kill/quiescence/removal sequence.
An empty legacy `_iotox_session_<pid>_<sequence>` leaf may be removed, but a populated legacy leaf or
malformed reserved name stops startup because PID-only ownership cannot be made reuse-safe after the
fact. Unreadable or ambiguous procfs evidence never authorizes cleanup.

### Composed host and profile resource budgets

rev0033 retains rev0030's five profile-scoped hard-budget fields and adds a sixth ordered soft
memory-throttle field to local profile v4. The matching command-line settings remain deployment-wide
policy:

```text
--ratox-cgroup-pids-max N
--ratox-cgroup-memory-high-bytes N
--ratox-cgroup-memory-max-bytes N
--ratox-cgroup-swap-max-bytes N
--ratox-cgroup-cpu-quota-us N
--ratox-cgroup-cpu-period-us N
```

At every admission, IoTox validates the host envelope and resolved profile budget, then computes one
effective budget before touching the cgroup filesystem. For process count, `memory.high`, hard memory maximum, and swap, an absent side inherits the
configured side and two configured values select the smaller maximum. The effective `memory.high` is
then clamped to the effective `memory.max` when both exist, so composition cannot produce an inverted
kernel policy even when the tighter high and hard ceilings come from different policy layers. Zero
swap remains meaningful and therefore wins over every positive swap maximum. For CPU bandwidth, IoTox
compares the exact positive `quota/period` rationals; the lower ratio wins. An omitted period means
100,000 microseconds. The comparison uses an overflow-free continued-fraction algorithm rather than
floating point or potentially overflowing cross-products. Equal ratios retain the host representation,
which keeps administrator-owned canonical policy stable.

This composition is deliberately monotone: a profile may tighten or add a limit but cannot weaken a
host limit. It mirrors the kernel's hierarchical cgroup-v2 model, where a delegated descendant cannot
override restrictions imposed by an ancestor. The explicit composition is still required because
IoTox writes both local policy layers into the same per-session leaf and must prove the exact value it
intends to enforce.

The fields map to `pids.max`, `memory.high`, `memory.max`, `memory.swap.max`, and `cpu.max`. Any
memory-controller policy also sets `memory.oom.group=1`. `none` is the only absent-value spelling.
Process maxima must be positive and fit host `pid_t`; `memory.high` and `memory.max` must be positive
and host-page aligned, and a high threshold may not exceed a hard maximum within one policy envelope;
swap maxima must be page aligned; quotas must be at least 1,000 microseconds and fit signed 64-bit kernel syntax; periods must be
1,000..1,000,000 microseconds and cannot exist without a quota.

Any enabled profile with a nonempty cgroup budget requires an explicit delegated cgroup-v2 root, even
when the host envelope is empty. A requested delegated root still requires baseline or strict
confinement, a non-root exact payload uid distinct from the daemon, cleared supplementary groups, and
the production POSIX factory. Disabled profiles may retain staged budgets without activating that
requirement.

Startup computes the effective budget of every enabled profile and deduplicates preflight work by the
pair `(payload identity, effective budget)`. Profiles sharing an identity but requesting different
limits therefore receive separate controller write/read-back probes. The host-incarnation lease remains
held before those probes, orphan recovery, listener publication, or network activation. A real session
recomputes the same composition and applies/read-backs every effective field before the blocked helper
is attached, so no alternate factory call can bypass the policy.

Runtime status exposes only aggregate truth:

```text
ratox-cgroup-host-budget-configured=<0|1>
ratox-cgroup-profile-budget-count=<enabled profile count>
ratox-cgroup-preflight-policy-count=<distinct identity/effective-budget count>
```

Profile IDs, identities, paths, commands, and terminal bytes are not published.

### Teardown-time kernel outcome evidence

rev0033 prefers protected read-only `pids.events.local` and `memory.events.local` descriptors for the
controllers selected by the effective session policy, falls back to hierarchical `pids.events` and
`memory.events` only when the local interfaces are unsupported, and opens `cpu.stat` for configured
CPU bandwidth. A brand-new leaf must report a zero baseline for every selected counter before the blocked helper is attached. After recursive
`populated=0` and before exact-inode removal, the supervisor parses the keyed kernel records and
captures one content-free session outcome. Unknown future keys are accepted, duplicate or malformed
keys fail parsing, and the currently required keys are explicit.

The outcome is returned once and accumulated with saturating arithmetic in the same factory-owned
state that already publishes aggregate admission truth. Outcome collection remains active even when
aggregate reservation ceilings are disabled. A read or parse failure never prevents proved-empty leaf
cleanup; it contributes one incomplete-outcome count and no partial counter values. If exact teardown
is not proved, no completed outcome is claimed.

Owner-private runtime status adds cumulative counters:

```text
ratox-cgroup-completed-session-outcomes=<u64>
ratox-cgroup-incomplete-session-outcomes=<u64>
ratox-cgroup-pids-limit-hits=<u64>
ratox-cgroup-memory-high-events=<u64>
ratox-cgroup-memory-max-events=<u64>
ratox-cgroup-memory-oom-events=<u64>
ratox-cgroup-memory-oom-kills=<u64>
ratox-cgroup-memory-oom-group-kills=<u64>
ratox-cgroup-cpu-usage-us=<u64>
ratox-cgroup-cpu-periods=<u64>
ratox-cgroup-cpu-throttled-periods=<u64>
ratox-cgroup-cpu-throttled-us=<u64>
```

These are cumulative kernel counters for completed exact session leaves. They are not sampled
utilization, pressure-stall metrics, latency guarantees, per-profile labels, payload identity, or
terminal content. Local event interfaces provide direct attribution when available. Because IoTox
session leaves are validated childless domains, hierarchical `pids.events` and `memory.events` remain
an attributable compatibility fallback for the exact session subtree.

`memory.high` is a throttle/reclaim boundary, not an OOM guarantee or hard reservation. Aggregate
memory admission therefore continues to charge the finite effective `memory.max`; a profile that sets
only `memory.high` is observable and kernel-enforced but does not invent a hard-memory reservation.

### Aggregate host reservation admission

rev0032 retains host-only command-line aggregate policy above the effective profile budget; it does not add fields
to the canonical profile record:

```text
--ratox-cgroup-aggregate-pids-max N
--ratox-cgroup-aggregate-memory-max-bytes N
--ratox-cgroup-aggregate-swap-max-bytes N
--ratox-cgroup-aggregate-cpu-quota-us N
--ratox-cgroup-aggregate-cpu-period-us N
```

For each configured aggregate dimension, every enabled profile's effective post-composition budget
must contain a finite matching maximum and must fit once under the aggregate ceiling. Startup proves
this before cgroup recovery or network activation. At production spawn, one factory-wide admission
controller resolves and atomically charges the complete exact process/memory/swap/CPU vector before
helper-path, filesystem, PTY, leaf, or process mutation. The CPU quota is normalized to the aggregate
period with exact rational comparison and GCD reduction; any fractional quota-microsecond result is
rejected rather than rounded. Capacity exhaustion returns `resource_exhausted` with no
partial charge. A move-only reservation token rolls back pre-spawn and proved-cleanup early returns
and stays owned by the session until recursive cgroup quiescence, exact leaf removal, and leader reap.
If post-spawn cleanup cannot prove both reap and exact removal, the token strands its full charge so
subsequent admission remains conservatively fail closed until restart recovery.

Owner-private runtime status adds:

```text
ratox-cgroup-aggregate-budget-configured=<0|1>
ratox-cgroup-aggregate-pids-configured=<0|1>
ratox-cgroup-aggregate-memory-configured=<0|1>
ratox-cgroup-aggregate-swap-configured=<0|1>
ratox-cgroup-aggregate-cpu-configured=<0|1>
ratox-cgroup-aggregate-pids-max=<u64|0 when absent>
ratox-cgroup-aggregate-memory-max-bytes=<u64|0 when absent>
ratox-cgroup-aggregate-swap-max-bytes=<u64; zero may be configured>
ratox-cgroup-aggregate-cpu-quota-max-us=<u64|0 when absent>
ratox-cgroup-aggregate-cpu-period-us=<u64|0 when absent>
ratox-cgroup-aggregate-active-reservations=<size>
ratox-cgroup-aggregate-peak-active-reservations=<size>
ratox-cgroup-aggregate-reserved-processes=<u64>
ratox-cgroup-aggregate-reserved-memory-bytes=<u64>
ratox-cgroup-aggregate-reserved-swap-bytes=<u64>
ratox-cgroup-aggregate-reserved-cpu-quota-us=<u64>
ratox-cgroup-aggregate-peak-reserved-processes=<u64>
ratox-cgroup-aggregate-peak-reserved-memory-bytes=<u64>
ratox-cgroup-aggregate-peak-reserved-swap-bytes=<u64>
ratox-cgroup-aggregate-peak-reserved-cpu-quota-us=<u64>
ratox-cgroup-aggregate-rejected-reservations=<u64>
ratox-cgroup-aggregate-stranded-reservations=<u64>
```

The configured booleans distinguish absent values from meaningful zero swap. CPU totals are quota
microseconds at the published aggregate accounting period, not sums of raw session quota fields. A
stranded count means that a cleanup path deliberately retained its complete exact charge because
post-spawn teardown was not proved; it does not assert that work remains live. The ledger accounts
configured maxima conservatively; it does not allocate physical memory or processor time, preallocate
PIDs, observe actual usage, or guarantee allocation success.

The design continues to assume one trusted local writer owns the delegated subtree, consistent with
the systemd delegation contract. It does not claim I/O throttling, PSI-driven admission, synchronized
CPU periods, parent-cgroup CPU enforcement, physical resource reservation, or protection from a
separate privileged co-writer.

## Confinement modes

### `compatibility`

Compatibility omits IoTox's seccomp and Landlock/MDWE layers. It exists for byte-compatible v1
migration and for fixed executables that cannot operate under the baseline filter. It is not the pre-rev0022
privilege boundary: the new common capability floor still applies.

### `baseline`

Baseline installs and verifies an architecture-checked classic BPF seccomp filter. Architecture
confusion terminates the process; x32 syscall numbers on x86-64 receive `ENOSYS`. After helper setup,
it denies `setsid`, controlling-terminal detach/reassignment, and parent-death-signal mutation so the
session-wide supervisor contract cannot be weakened through those reviewed paths. The filter denies a
bounded set of high-risk process-inspection, kernel-extension, asynchronous-kernel, mount/namespace,
module/kexec/reboot/swap, handle/keyring, privileged-I/O, kernel-log/accounting, fanotify,
personality, host-identity, and time-mutation syscalls with `EPERM`.

rev0024 adds `pidfd_open`, `pidfd_send_signal`, `process_madvise`, and `process_mrelease` to the
payload deny floor. Those process-handle operations remain parent-supervisor responsibilities; the
final target has no need to acquire or operate a new pidfd through the reviewed interfaces.

rev0023 also inspects selected syscall arguments. For `ioctl(2)`, it denies terminal-input injection,
line-discipline and console redirection, reviewed keyboard/font mutations, and virtual-terminal
switch/resize/lock requests while leaving ordinary termios and window operations available. For
legacy `clone(2)`, it denies mount, cgroup, UTS, IPC, user, PID, and network namespace flags. Because
classic BPF cannot dereference `clone3(2)`'s pointed-to argument structure, baseline returns `ENOSYS`
for clone3 so libc can retry the inspected legacy path. Ordinary thread creation is exercised after
filter installation.

The filter allows every syscall not named by that deny policy. Baseline is therefore a hazardous-
interface floor, not a complete allowlist or network/filesystem sandbox.

### `strict`

Strict includes baseline and requires all of these before the child announces readiness:

```text
PR_MDWE_REFUSE_EXEC_GAIN armed and verified
Landlock ABI >= 10
Landlock thread-synchronized enforcement
baseline seccomp filter installed and verified
```

Unsupported, disabled, or externally filtered primitives reject the spawn. There is no silent
fallback to baseline or compatibility.

Strict handles all ABI-10 filesystem mutation rights, device ioctl, pathname UNIX-socket resolution,
TCP bind/connect, UDP bind/connect-send, abstract UNIX sockets, and signals. It grants normal
mutation only beneath the already-open working directory. Character/block device creation remains
denied there. No external network port is allowed. External pathname or abstract UNIX socket access
and signals outside the Landlock domain are denied.

Strict does not handle filesystem read or execute rights. A target can read and execute wherever DAC
and the host's other policies permit. The PTY stdio descriptors were opened before Landlock and are a
deliberate inherited interface. Every unreserved helper descriptor is closed.

A strict working directory cannot be `/`.

## Operator selection

Use `baseline` for the ordinary reviewed default. Select `compatibility` only after documenting the
specific denied interface required by the fixed target. Select `strict` when the target should write
only beneath its working tree and requires no external TCP/UDP, external UNIX-socket, or external
signal operation, and when the deployment kernel is qualified for Landlock ABI 10 and MDWE.

Profile mode is local operator policy. Remote authority never upgrades or downgrades it.

## Evidence and limitations

The native process tests prove the common capability floor, argument-aware baseline filter, ordinary
ioctl/fork/thread compatibility, lifecycle-property freezes, high inherited descriptor closure,
required pidfd retention, process-handle syscall denial, repeated quiescence before leader reap,
separate-process-group fork-churn shutdown, and natural-leader orphan cleanup. On an ABI-10 host, the
strict branch proves one working-tree write and denial of outside write, TCP, UDP, external pathname
UNIX socket, external signal, and executable-permission gain. On a host where any strict primitive is
unavailable, the same oracle requires a named fail-closed startup result and proves the target did not
run.

Without `--ratox-cgroup-root`, none of the modes supplies delegated-cgroup lifecycle semantics. With
it, the supervisor supplies the exact create/recover/attach/kill/populated/remove contract above and,
when explicitly configured, kernel-enforced process, memory, swap, and CPU ceilings. It does not
supply I/O-controller policy, PSI-driven adaptation, synchronized CPU periods, parent CPU enforcement, physical resource
reservation, protection from another privileged writer, or target-fleet qualification. No mode supplies a created
PID/user/mount namespace
sandbox, a read allowlist, mount isolation, proof against unknown future session escapes, VM
isolation, same-UID executable-content immutability, PTY survival across daemon restart, or
public-network qualification. “Strict” names this precise local kernel contract; it does not mean a
complete sandbox.
