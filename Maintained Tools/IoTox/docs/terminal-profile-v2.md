# IoTox local terminal profile v2

> Historical compatibility contract. The encoder emits canonical profile v7; canonical v2 records
> remain accepted, decode with an empty profile-scoped cgroup budget, and never invent I/O policy,
> account groups, privilege, or payload pins. See `terminal-profile-v7.md`.

Status: implemented in rev0022, argument-hardened in rev0023, process-domain-hardened in rev0024,
optionally cgroup-lifecycle-hardened in rev0025, joined through message-bound local IPC in rev0026,
served through bounded local admission in rev0027, crash-orphan-recoverable in rev0028, and optionally resource-bounded in rev0029 behind the
explicit default-off Ratox host gate
Wire effect: none; terminal profiles remain operator-owned local policy and are never selected by
remote bytes
Historical role: v2 was the canonical encoder format; canonical v1 remains accepted as explicit
`compatibility` mode, and rev0033 supersedes v2 emission with canonical v4

## Purpose

A terminal profile freezes every local process-selection input for one authorized Ratox OPEN:
executable, arguments, working directory, environment, terminal type, window policy, identity,
resource limits, shutdown timing, and kernel confinement tier. A remote peer can request terminal
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

The canonical v2 profile record has exactly one LF-terminated line per field, exact field order, no
unknown or duplicate singleton fields, lowercase even-length hexadecimal, canonical unsigned decimal,
and byte-for-byte decode/re-encode equality. Arguments, cwd, and environment values remain
hex-encoded.

## Profile record grammar

```text
iotox-terminal-profile-v2
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
iotox-terminal-profile-v2
id=maintenance-shell
enabled=1
argument-hex=2f62696e2f6563686f
argument-hex=666978656420617267756d656e74
working-directory-hex=2f7661722f6c69622f696f746f782f776f726b
terminal-type=xterm-256color
inherit-environment=LANG
inherit-environment=TZ
environment-hex=ALPHA:6669727374
identity=inherit
confinement=strict
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

The decoder accepts both exact headers:

```text
iotox-terminal-profile-v1
iotox-terminal-profile-v2
```

A canonical v1 record has no confinement field and decodes as
`confinement=compatibility`. Its own bytes are checked against the v1 canonical encoder, so a malformed
or hybrid v1/v2 record is rejected. The public encoder always emits v2. Saving or otherwise
re-encoding a loaded v1 profile therefore creates an explicit v2 compatibility record rather than
silently applying the new default.

New C++ `Profile` values default to `baseline`.

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

### Optional controller-backed host envelope

rev0029 adds a host-global deployment policy, not a profile field or remote selector:

```text
--ratox-cgroup-pids-max N
--ratox-cgroup-memory-max-bytes N
--ratox-cgroup-swap-max-bytes N
--ratox-cgroup-cpu-quota-us N
--ratox-cgroup-cpu-period-us N
```

Configured fields map to `pids.max`, `memory.max`, `memory.swap.max`, and `cpu.max` on every session
leaf. Memory or swap policy also sets `memory.oom.group=1`. Zero swap is an explicit no-swap policy;
memory and swap byte counts must be host-page aligned; a CPU quota without a period uses 100,000
microseconds; and a period without a quota is invalid. Limits without an explicit delegated root fail
before profile-store, lease, recovery, or network work.

Every requested controller must appear in both the delegated root's `cgroup.controllers` and
`cgroup.subtree_control`. Startup preflight and real session creation prove the control files are
daemon-owned and payload-unwritable, apply every configured value, and read it back exactly. A real
session completes that proof before the blocked helper is attached. Missing or inactive controllers,
threaded topology, malformed records, normalized values, unsafe ownership, or probe cleanup failure
never downgrade to lifecycle-only containment.

This design assumes one trusted local writer owns the delegated subtree. It does not attempt to
defend against a separate privileged manager concurrently moving processes into the leaf.

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
supply I/O-controller policy, PSI-driven adaptation, per-profile or aggregate host budgeting,
protection from another privileged writer, or target-fleet qualification. No mode supplies a created
PID/user/mount namespace
sandbox, a read allowlist, mount isolation, proof against unknown future session escapes, VM
isolation, same-UID executable-content immutability, PTY survival across daemon restart, or
public-network qualification. “Strict” names this precise local kernel contract; it does not mean a
complete sandbox.
