# IoTox cloudtainer build report — rev0022

**Date:** 2026-08-17 America/New_York
**Version:** 0.22.0
**Revision:** rev0022
**Codename:** Attested Confinement Citadel
**Linked handoff revision:** rev0009

## 1. Scope

rev0022 advances two security-critical boundaries without claiming evidence that was not produced.

First, it replaces the R7 analyzer's asserted-duration input with a reconstructable, tamper-evident
capture chain. A deterministic balanced schedule identifies every route/load trial. Raw
controller-local and host-local steady timestamps are retained and all qualification intervals are
re-derived without cross-host clock subtraction. Exact Ratox message, sequence, byte-span, and event
coordinates join protocol admission, whole-frame PTY input commitment, and output publication while
retaining no terminal content. Canonical schedule, sample, route, and bulk-artifact digests are bound
by two distinct role-separated ephemeral Ed25519 signatures.

Second, it substantially hardens the native PTY target. Every profile mode receives a verified
capability and credential floor. Canonical terminal profile v2 adds explicit compatibility, baseline,
and strict tiers. Baseline installs an architecture-checked seccomp hazardous-interface deny floor.
Strict additionally requires MDWE and Landlock ABI 10 and fails closed rather than silently
weakening policy.

This report records local construction and deterministic validation. No public-Tox qualification,
two-physical-host R7 result, remote hardware attestation, target-kernel fleet qualification, or
hardware power-cut durability result was created or claimed.

## 2. Attested R7 evidence chain

### Reconstructable schedule

`tools/prepare-ratox-r7.py` and `tools/ratox_r7_evidence.py` construct a deterministic schedule over
two route classes and six bulk-load classes. Every twelve-trial block contains each cell exactly once.
A domain-separated SHA-256 counter stream, unbiased rejection sampling, Fisher-Yates ordering, and a
run/seed/ordinal/route/load-bound trial token make the order independently reconstructable.

### Raw same-clock timing

The v2 measurement schema retains three controller and three host steady-clock coordinates. The
analyzer derives all gate inputs from those coordinates, checks local monotonicity within and across
samples, and never orders or subtracts values across hosts. Controller and host stage distributions
are reported separately.

### Exact content-free Ratox joins

`RatoxServiceEvent` now carries the message ID, current and next sequence coordinates, byte count, and
event ordinal needed to identify one input admission, one whole-frame terminal commit, or one output
append. Runtime projection and tests preserve coordinates while continuing to reject terminal bytes,
argv, environment, working directories, profile IDs, and setup error strings from lifecycle evidence.

### Canonical digest and signature boundary

The unsigned evidence bundle binds canonical schedule and sample bytes plus exact sizes and SHA-256
digests for distinct retained route and bulk-observation files. Two separate ephemeral Ed25519 keys
sign role-separated payloads containing the same complete unsigned run. Signing checks the local
Linux boot ID and verifies that the supplied secret key derives the advertised public key. Sealing and
analysis independently verify both signatures and require the auxiliary files again.

This is software capture attestation and tamper evidence. It is not measured boot, hardware identity,
proof of physical host count, proof of route truth, or proof that both operators were uncompromised.

### File and parser hardening

The evidence tools enforce bounded ASCII, canonical integers, exact schemas, finite line/row/file
sizes, no-follow regular-file reads, pre/post identity and mutation checks, owner-private secret-key
files, distinct auxiliary evidence inodes/content, exclusive 0600 output creation, and file plus
containing-directory synchronization.

## 3. Terminal capability and confinement construction

### Common floor

Every terminal mode now:

```text
discovers a bounded runtime capability ceiling
clears and verifies ambient capabilities across that ceiling
clears and verifies effective, permitted, and inheritable capability sets
sets and verifies no_new_privs
keeps the privileged helper handoff nondumpable
closes every nonreserved descriptor before target exec
```

When effective `CAP_SETPCAP` is available, the helper additionally locks root/set-ID/keep-caps/ambient
securebits, drops the complete capability bounding set, and verifies the result after any identity
transition. A privileged launch that cannot establish the required seal fails before target code runs.

### Canonical profile v2

Terminal profiles now encode one explicit confinement field:

```text
confinement=compatibility|baseline|strict
```

Canonical v1 records remain readable and map only to explicit compatibility mode. New profile values
default to baseline. Re-encoding a v1 record produces an explicit v2 compatibility record rather than
silently changing its syscall behavior.

### Baseline seccomp tier

Baseline installs a classic BPF filter after `no_new_privs`. It validates the audit architecture,
terminates on architecture confusion, returns `ENOSYS` for x32 syscall numbers on x86-64, and returns
`EPERM` for a bounded reviewed set of hazardous process-inspection, kernel-extension, mount/namespace,
module, keyring, privileged-I/O, host-mutation, and clock-mutation interfaces.

The policy intentionally allows syscalls not named by the deny floor. It is not represented as a
complete allowlist, container, or sandbox.

### Strict tier

Strict includes baseline and requires all of the following before readiness:

```text
PR_MDWE_REFUSE_EXEC_GAIN armed and verified
Landlock runtime ABI 10 or newer
complete ABI-10 ruleset populated and thread-synchronized
baseline seccomp filter installed and verified
```

The Landlock policy handles filesystem mutation rights through ABI 10, device ioctl, pathname and
abstract UNIX sockets, TCP/UDP actions, and signals. Ordinary mutation is granted only beneath the
already-open non-root working directory; character/block-device creation remains denied. No network
port rule is granted. Read and execute access are deliberately outside this policy.

Unsupported or externally filtered MDWE, Landlock, or seccomp primitives produce a named fail-closed
startup result. Strict never silently downgrades.

## 4. Defects found and fixed during construction

1. The first ASan/UBSan process run failed before the PTY readiness handshake. The process fixture had
   correctly applied a 512 MiB address-space limit, but an ASan-instrumented re-exec requires its
   multi-terabyte shadow reservation. Only the ASan helper lane now disables that one finite limit;
   GCC, Clang, release, and ordinary product lanes continue to test it.
2. GCC 14 Release with warnings-as-errors diagnosed a libstdc++ iterator-inlining null-dereference in
   a newly added test-only file-read expression. The assertion now uses an explicit checked bounded
   read loop, eliminating optimizer-dependent diagnostic behavior without weakening the test.
3. The first ThreadSanitizer combined invocation stalled when the large fork/exec lifecycle test ran
   immediately after 28 parallel instrumented tests. The same binaries completed cleanly when the
   28-test non-process group and the one lifecycle process oracle were run as explicit isolated lanes.
   The retained evidence reports those invocations separately rather than disguising runner coupling.
4. Packaging documentation still described the historical hidden `.datacube/` handoff even though the
   active packager emits a verified commit-addressed repository datacube. The active contract now
   matches the implementation and preserves the old layout only as history.
5. rev0022 documentation initially retained the previous 292-check count. The final owned registry is
   293/293 and all active validation records now use the measured value.

## 5. Toolchain and built identity

```text
Linux 6.18.35 x86_64
GCC 14.2.0
Clang 17.0.0
CMake 3.31.6
Ninja 1.12.1
Python 3.13.5
Git 2.47.3
IoTox 0.22.0 rev0022
```

The build container did not expose `/sys/kernel/security/landlock/abi`; the strict native process
oracle therefore remains the authoritative enforced-or-fail-closed host test rather than an assumed
sysfs capability claim.

## 6. Compiler and deterministic test evidence

### GCC Debug, warnings as errors

```text
owned registry: tests=293 selected=293 shard=0/1 failures=0
CTest: 14/14 passed
```

### Clang Debug, warnings as errors

```text
CTest: 14/14 passed
```

### GCC Release, warnings as errors

```text
CTest: 14/14 passed
native terminal confinement process oracle: 100 consecutive passes
```

### Clang AddressSanitizer and UndefinedBehaviorSanitizer

The sanitizer preset used sixteen deterministic owned-registry shards plus all process, CLI, and
analyzer targets:

```text
CTest: 29/29 passed
```

No ASan or UBSan diagnostic was emitted in the retained final run.

### GCC ThreadSanitizer

The instrumented surface passed in two explicit invocations:

```text
non-lifecycle group: 28/28 passed
binary process lifecycle: 1/1 passed
```

No TSan diagnostic was emitted in either retained final invocation.

### Python evidence tooling

```text
py_compile: passed
ratox-r7-analyzer self-test: PASS
```

The analyzer self-test covers a valid 12,000-sample signed bundle and deterministic report, then
rejects edited samples, signature corruption, schedule/order faults, globally reordered host events,
changed auxiliary evidence, evidence aliasing, symlink inputs, malformed canonical values, and
bounded-file violations.

## 7. Retained evidence

```text
artifacts/rev0022/gcc-debug-configure.log
artifacts/rev0022/gcc-debug-build.log
artifacts/rev0022/gcc-debug-ctest.log
artifacts/rev0022/gcc-debug-owned-registry.log
artifacts/rev0022/clang-debug-configure.log
artifacts/rev0022/clang-debug-build.log
artifacts/rev0022/clang-debug-ctest.log
artifacts/rev0022/gcc-release-configure.log
artifacts/rev0022/gcc-release-build.log
artifacts/rev0022/gcc-release-ctest.log
artifacts/rev0022/gcc-release-terminal-confinement-repeat100.log
artifacts/rev0022/clang-asan-ubsan-configure.log
artifacts/rev0022/clang-asan-ubsan-build.log
artifacts/rev0022/clang-asan-ubsan-ctest.log
artifacts/rev0022/gcc-tsan-configure.log
artifacts/rev0022/gcc-tsan-build.log
artifacts/rev0022/gcc-tsan-nonbinary-ctest.log
artifacts/rev0022/gcc-tsan-binary-process-ctest.log
artifacts/rev0022/python-compile.log
artifacts/rev0022/ratox-r7-analyzer-self-test.log
artifacts/rev0022/toolchain-and-identity.txt
artifacts/rev0022/validation-summary.txt
artifacts/rev0022/SHA256SUMS
artifacts/reports/validation-summary.txt
```

Detailed implementation and source review live in:

```text
docs/research/ratox-r7-attested-evidence-chain-rev0022.md
docs/research/terminal-confinement-rev0022.md
docs/decisions/0071-bind-ratox-r7-to-attested-raw-evidence.md
docs/decisions/0072-seal-terminal-capabilities-and-add-tiered-kernel-confinement.md
```

## 8. Research boundary and nonclaims

Primary references were rechecked for Ed25519 detached signatures, Linux boot IDs, same-clock delay
measurement, descriptor-relative file handling, capabilities, securebits, `no_new_privs`, seccomp,
MDWE, Landlock ABI 10, dumpability, and exec behavior. They define upstream semantics and do not audit
IoTox.

rev0022 does not prove public Tox bootstrap or NAT traversal, relay reliability, route identity,
physical host count, clock calibration, load-generator truth, two-host R7 latency, production CPU/RSS
or power targets, hardware power-cut durability, complete sandboxing, filesystem read secrecy, mount
or namespace isolation, whole-descendant resource ownership, rollback resistance against an
equivalent owner, or production support readiness.

The next evidence-bearing R7 action remains a retained two-physical-host execution of the canonical
schedule with independently reviewed route/load procedure artifacts. Deployment work must separately
qualify strict mode on each target kernel and service-manager policy rather than infer support from this
build host.
