# Linux terminal capability and confinement review — rev0022

Date: 2026-08-17
Status: implemented and locally validated; strict-mode runtime enforcement depends on host kernel
Codename: Attested Confinement Citadel

## Question

How can IoTox substantially harden its native PTY target without converting a bounded local process
boundary into an unsupported complete-sandbox claim, and without silently changing existing v1
profile behavior?

## Primary source review

Rechecked on 2026-08-17:

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

Applied interpretation:

- capability sets are independent; clearing ambient capabilities alone does not prove empty
  effective, permitted, inheritable, or bounding sets;
- `SECBIT_NOROOT` and locked securebits are needed to prevent UID 0 from recovering traditional root
  capability semantics across exec;
- `no_new_privs` is persistent and blocks privilege gain through later exec, but does not itself
  filter syscalls or ordinary filesystem/network access;
- a seccomp filter must validate the syscall architecture, and x86-64 policy must account for x32;
- Landlock ABI 10 adds UDP actions, ABI 9 adds pathname UNIX-socket resolution, ABI 8 adds synchronized
  enforcement, ABI 6 adds signal/abstract-UNIX scopes, and ABI 5 adds device ioctl control;
- Landlock rights associated with a file descriptor depend on when it was opened, so inherited PTY
  stdio remains a deliberate exception while unreserved handoff descriptors are closed before exec;
- MDWE prevents later executable-permission gain but does not replace a complete memory-safety or JIT
  policy;
- `PR_SET_DUMPABLE=0` can be reset by exec and must be documented as a helper-handoff guard.

The current kernel documentation is dated June 2026 and describes ABI 10. The current upstream UAPI
header was used to verify the exact ABI 8/9/10 wire values not present in this build image's older
userspace header. IoTox carries a fixed-width ruleset prefix, packed path-rule record, and named local
constants for those reviewed values, with compile-time equality checks whenever the build header
exports the same names. Runtime ABI discovery remains authoritative. Upstream documentation and
headers are design inputs, not an IoTox audit.

## Construction

### Runtime capability ceiling

The helper probes `PR_CAPBSET_READ` until `EINVAL`, capped at 1,024 to keep the operation bounded. It
refuses a capability ceiling outside the 64-bit version-3 `capget` layout rather than assuming a future
kernel remains representable. Ambient readback and bounding-set drop use this runtime ceiling instead
of the build-time `CAP_LAST_CAP`.

### Privileged seal

A helper with effective `CAP_SETPCAP` locks root and set-ID capability semantics, disables keep-caps,
locks ambient raising, drops every bounding member, and verifies the result. A privileged UID or
nonempty capability context that cannot perform that seal is rejected. After exact/inherited identity
handling, `capset` installs zero effective, permitted, and inheritable sets and the helper rechecks all
state before exec.

This ordering retains only the capabilities needed to perform an explicitly configured identity
transition and then destroys them before target code runs.

### Tiered profile semantics

Canonical profile v2 adds `confinement=compatibility|baseline|strict`. Compatibility still receives
all common process and capability hygiene. Baseline adds an architecture-checked seccomp hazardous-
interface deny filter. Strict adds MDWE and a no-downgrade Landlock ABI 10 domain before installing the
same seccomp filter. Canonical v1 records decode only as compatibility.

### Baseline filter

The classic BPF program kills architecture confusion, returns `ENOSYS` for x32 on x86-64, denies a
reviewed bounded set of process-inspection, kernel-extension, asynchronous-kernel, mount/namespace,
module, reboot/swap, handle, keyring, privileged-I/O, kernel-log/accounting, fanotify, personality,
host identity, and time-mutation syscalls, then allows everything else. A post-install `PR_GET_SECCOMP`
check proves filter mode.

The filter is intentionally not a complete allowlist. In particular, it does not claim to prohibit all
namespace creation through every clone ABI, all networking, all filesystem access, or all descendant
escape techniques.

### Strict Landlock policy

The ruleset handles:

```text
filesystem write/remove/make/refer/truncate
character/block-device creation (handled but never granted)
device ioctl
pathname UNIX-socket resolution
TCP bind/connect
UDP bind/connect-send
abstract UNIX-socket and signal scopes
```

Only ordinary mutation below the already-open working directory is granted. `/` is invalid as a
strict writable root. No TCP or UDP port is granted. Read and execute rights are not handled. The
policy is enforced with the ABI 8 thread-sync flag; strict requires ABI 10 so no compatibility masking
or partial mode exists.

### Startup diagnostics

The child protocol's valid stage range was extended through the new controls. Capability preparation
and finalization now retain the exact ambient, securebits, bounding-set, active-set, or identity stage
that failed instead of collapsing every capability error into one generic report. This also fixes a
latent rev0021 diagnostic bug: the ambient-capability stage value was outside the old validator's upper
bound and could be misclassified as a malformed child record.

## Validation performed in this build environment

The GCC warnings-as-errors build and all default CTest targets pass. The native PTY process oracle
proves baseline filter operation, zero active and ambient capabilities, exact-identity behavior, root
bounding-set removal and securebits locking, inherited ambient-capability destruction, descriptor
hygiene, and parent-death behavior.

The build container reports a Linux 6.18.35 kernel string, but its outer syscall policy returns
`ENOSYS` for the Landlock ABI query. Therefore the local strict test exercises the required named
fail-closed Landlock startup path and verifies that target code did not mutate either outside test
file. The same test contains a runtime-enforcement branch for an ABI 10 host. It requires allowed
in-tree regular-file creation, cross-directory rename/truncate/unlink, and pathname-UNIX bind; denial
of out-of-tree create/truncate/unlink; denial of TCP connect/bind, UDP send/connect/bind,
pathname-UNIX connect, abstract-UNIX connect, and external signals; plus MDWE and baseline seccomp
denial. That branch was constructed but was not reached in this container.

Sanitizer and retained matrix results are recorded separately in `artifacts/rev0022/` and the rev0022
build report.

## Findings and nonclaims

1. Runtime capability discovery is safer than a compiled `CAP_LAST_CAP`, but future capability APIs
   larger than the version-3 layout are intentionally unsupported until reviewed.
2. An unprivileged process cannot normally empty its bounding set. Empty active/ambient sets plus
   `no_new_privs` remain the enforceable floor; root/privileged launches are required to prove the
   stronger complete seal.
3. Landlock is stackable. An outer container may make it unavailable, and strict mode must reject
   rather than downgrade.
4. Device ioctl control does not remove the deliberately inherited PTY stdio descriptors; they were
   opened before the Landlock domain. All other handoff descriptors are close-on-exec and explicitly
   closed.
5. Baseline seccomp is a deny filter, not proof of a complete syscall inventory.
6. Strict mode restricts mutation and named network/IPC operations but does not hide readable files or
   restrict execution paths.
7. No cgroup, PID/user/mount namespace, service-manager sandbox, VM, whole-descendant resource quota,
   public-network experiment, or two-physical-host terminal qualification is claimed.
