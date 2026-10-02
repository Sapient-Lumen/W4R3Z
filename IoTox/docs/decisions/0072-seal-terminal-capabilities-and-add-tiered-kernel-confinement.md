# ADR 0072: Seal terminal capabilities and add tiered kernel confinement

Status: accepted
Date: 2026-08-17

## Context

The rev0017 terminal boundary already fixed executable, argv, cwd, environment, identity, rlimits,
PTY ownership, descriptor hygiene, startup proof, and parent-death behavior. It set and verified
`no_new_privs` and cleared ambient capabilities, but it did not clear the effective, permitted, or
inheritable sets, empty the capability bounding set when possible, lock securebits, filter hazardous
syscalls, or restrict filesystem/network/IPC operations. Calling that boundary a sandbox would have
been false.

The R8 decision must improve the default without silently changing canonical v1 policy bytes into an
unreviewed strict sandbox. It must also avoid a best-effort strict mode that appears enabled after one
or more required kernel controls failed.

Primary Linux references rechecked for this decision:

```text
https://man7.org/linux/man-pages/man7/capabilities.7.html
https://man7.org/linux/man-pages/man2/capget.2.html
https://man7.org/linux/man-pages/man2/PR_SET_SECUREBITS.2const.html
https://docs.kernel.org/userspace-api/no_new_privs.html
https://docs.kernel.org/userspace-api/seccomp_filter.html
https://man7.org/linux/man-pages/man2/seccomp.2.html
https://docs.kernel.org/userspace-api/landlock.html
https://raw.githubusercontent.com/torvalds/linux/master/include/uapi/linux/landlock.h
https://man7.org/linux/man-pages/man2/PR_SET_MDWE.2const.html
https://man7.org/linux/man-pages/man2/PR_SET_DUMPABLE.2const.html
https://man7.org/linux/man-pages/man2/execve.2.html
```

These sources define kernel interfaces and semantics. They do not audit IoTox or establish that every
Linux distribution enables the required features.

## Decision

### Common capability and handoff floor

Every native terminal mode, including compatibility mode, keeps the existing descriptor-opened ELF,
canonical manifest, exact environment, PTY, identity, rlimit, parent-death, and `no_new_privs`
contracts. Before final exec, the reviewed helper additionally:

1. discovers the running kernel's capability ceiling with `PR_CAPBSET_READ` rather than trusting the
   build header's `CAP_LAST_CAP`;
2. rejects a future capability ceiling that no longer fits the reviewed version-3 `capget` layout;
3. clears and reads back every ambient capability through that runtime ceiling;
4. when effective `CAP_SETPCAP` is available, sets and locks `SECBIT_NOROOT`, locks set-UID fixup and
   keep-caps off, locks ambient raising off, drops every bounding-set member, and reads the result back;
5. refuses a privileged UID or nonempty capability context that cannot establish that seal;
6. after optional identity transition, clears effective, permitted, and inheritable capability sets,
   reads them back, clears ambient capabilities again, and re-verifies every seal;
7. sets `PR_SET_DUMPABLE=0` during the privileged helper handoff, before and after credential work.

The dumpable guard protects the helper setup interval. A normal `execve` may reset dumpability for the
new program, so IoTox does not claim that the final target remains nondumpable.

An already-unprivileged target may be unable to empty its inherited bounding set because the kernel
requires `CAP_SETPCAP`. It still reaches exec only with empty active and ambient sets plus
`no_new_privs`; file capability and set-ID exec cannot grant new privilege. The runtime report states
whether the stronger root/privileged bounding-set and securebits seal was established.

### Canonical profile v2 and three modes

The encoder now emits `iotox-terminal-profile-v2` with one required field after identity:

```text
confinement=compatibility|baseline|strict
```

New in-memory profiles default to `baseline`. The decoder continues to accept byte-canonical v1
records and maps them to explicit `compatibility`, preserving their previous syscall behavior. A v1
record is never silently interpreted as strict. Re-encoding a loaded v1 profile is an explicit v2
migration.

The modes are:

- `compatibility`: common capability/credential/descriptor floor, but no IoTox seccomp or Landlock
  layer;
- `baseline`: common floor plus the reviewed architecture-checked seccomp deny filter;
- `strict`: baseline plus fail-closed MDWE and Landlock ABI 10 policy.

Strict mode rejects `/` as its writable working directory because granting the mutation set beneath
root would collapse the filesystem boundary.

### Baseline seccomp contract

The helper installs a classic BPF seccomp filter only after `no_new_privs`. It validates
`seccomp_data.arch` and kills on architecture mismatch. On x86-64 it returns `ENOSYS` for the x32
syscall range. It returns `EPERM` for a bounded reviewed set of high-risk interfaces, including:

```text
ptrace, process_vm_*, pidfd_getfd, kcmp
bpf, perf_event_open, userfaultfd, io_uring_*
mount/umount/pivot_root and the new mount API
chroot, unshare, setns
module, kexec, reboot, swap, handle, keyring, I/O-port, kernel-log, accounting,
quota, dcookie, fanotify, personality, hostname/domain-name, and clock mutation calls
```

All other syscalls remain allowed. The filter is therefore a hazardous-interface floor, not a
complete syscall allowlist and not a container boundary. Explicit compatibility mode exists for a
fixed target that cannot operate under the baseline filter.

### Strict MDWE and Landlock contract

Strict mode is all-or-nothing. Spawn fails at a named setup stage unless:

- `PR_MDWE_REFUSE_EXEC_GAIN` can be armed and read back;
- Landlock reports ABI 10 or newer;
- the complete ruleset can be created, populated, and enforced with thread synchronization; and
- the baseline seccomp filter can be installed and read back.

The Landlock layer handles all filesystem mutation rights known through ABI 10, device ioctl, pathname
UNIX-socket resolution, TCP bind/connect, UDP bind/connect-send, abstract UNIX sockets, and signals.
It grants ordinary file/directory mutation only beneath the already-open non-root working directory.
Character and block device creation is denied even there. No network port rule is granted. Pathname
UNIX sockets created outside the new domain, abstract sockets outside the domain, and signals to
processes outside the domain are denied. Read and execute access are intentionally not handled by this
profile, and the PTY stdio descriptors were opened before enforcement.

Landlock, MDWE, seccomp, `no_new_privs`, and capability restrictions are inherited by descendants and
cannot be removed by the target. IoTox still does not own escaped descendants through cgroups or PID
namespaces, and it does not claim read secrecy, mount isolation, resource accounting for the whole
process tree, or a virtual-machine boundary.

### Evidence and diagnostics

The native process oracle now reports and checks:

```text
ambient/effective/permitted/inheritable capability counts
bounding-set count and securebits seal
no_new_privs and seccomp mode
one syscall known to be denied by baseline
MDWE state and post-exec dumpability as observations, not overclaims
```

Root and inherited-ambient-capability lanes require the complete bounding-set/securebits seal. Strict
coverage is portable across build hosts: when the kernel supports the contract, the fixture proves
in-tree create/rename/truncate/unlink and pathname-UNIX bind, while denying out-of-tree
create/truncate/unlink, TCP connect/bind, UDP send/connect/bind, external pathname and abstract UNIX
connect, external signal, executable-memory gain, and the baseline syscall. When the build
environment blocks or lacks a required primitive, the same test requires a named fail-closed MDWE,
Landlock, or seccomp startup result and proves the target did not run or mutate the outside sentinel.

## Consequences

The default terminal profile is materially safer than rev0021 while legacy v1 policy retains explicit
compatibility semantics. Privileged helper state cannot accidentally flow into the final target, and a
root target cannot regain ordinary root capabilities through exec after the complete seal is applied.
Strict mode gives operators a precise ABI-dependent write/network/IPC/MDWE contract instead of a
vague “sandbox” switch.

Some programs will require compatibility mode because baseline deliberately denies interfaces they
use. Strict mode requires a current Landlock ABI 10 kernel and may be unavailable inside containers or
service sandboxes whose outer seccomp policy blocks Landlock. This is a supported fail-closed result,
not a downgrade.

## Rejected alternatives

- **Keep ambient clearing only.** Effective, permitted, inheritable, bounding, and root-exec behavior
  would remain materially under-specified.
- **Apply strict mode best effort.** A profile could appear strict after silently omitting UDP,
  pathname UNIX, signal, MDWE, or filesystem controls.
- **Silently reinterpret v1 records as baseline or strict.** Existing canonical bytes would change
  behavior without an explicit policy-version transition.
- **Use one universal seccomp allowlist now.** IoTox does not yet have a complete per-target syscall
  inventory, and a false complete-sandbox claim would be worse than the bounded deny filter.
- **Grant all mutation rights under the working directory.** Character and block device creation is
  unnecessary for the terminal profile and remains denied.
- **Call the result a complete sandbox.** There are no namespaces, cgroups, mount graph, whole-tree
  resource ownership, read allowlist, or hardware/VM boundary.
