# Optional unikernel lane (Solo5 / MirageOS / rump kernels as lessons)

DeriveBSD is microVM-first, but the workload payload does not *have* to be a “full OS userland”.
There is a useful (optional) lane where the runtime image is closer to a **unikernel / library-OS**:
minimal surface area, explicit host resource declarations, and fast boot.

This is not a default. It is a **target type** for specific workloads where reducing the runtime TCB is worth the tradeoffs.

References:
- Solo5 architecture (tender loads the unikernel and mediates access to declared host resources; includes an explicit application manifest concept): https://github.com/Solo5/solo5/blob/main/docs/architecture.md
- Solo5 overview: https://github.com/Solo5/solo5
- MirageOS overview (typed, modular unikernels): https://mirage.io/
- Building MirageOS unikernels with Nix (reproducible unikernel builds as a systems workflow): https://tarides.com/blog/2022-12-14-hillingar-mirageos-unikernels-on-nixos/
- NetBSD rump kernels tutorial (kernel components in userspace): https://www.netbsd.org/docs/rump/sptut.html
- NetBSD rump sysproxy/rumphijack (redirect syscalls to a rump server with per-process policy): https://www.netbsd.org/docs/rump/sysproxy.html

## Lessons to steal

### 1) “Declare resources” as a runtime contract

Unikernel systems stay operable when the runtime contract is explicit:
- which block devices exist
- which network interfaces exist
- which metadata/config channels exist

DeriveBSD can treat this as a derived artifact:
- `runtime.contract.json` emitted at Plan→Artifact time
- referenced by launch-time policy
- “why did this workload have access to X?” is answered by showing the contract + the policy decision

This plugs into the broader “interfaces are registries + diffs” posture:
- the unikernel manifest is a **contract source**
- it should show up in blast-radius diffs when it changes

See: `docs/94-runtime-blast-radius-contract.md`, `docs/370-contract-registries-and-api-diff-gates.md`.

### 2) Separate “bytes” from “execution wrapper”

A Solo5-style tender is a good mental model even if DeriveBSD implements it differently:
- **payload bytes** (the unikernel image)
- **execution wrapper** (the minimal host-side loader/mediator)

This matches DeriveBSD’s principle: *treat builders hostile* and minimize the trusted runtime.

### 3) Typed composition beats shell glue (MirageOS ergonomics)

MirageOS’s core win is not just “small images,” it’s **typed, modular composition** of the stack.
DeriveBSD should enable a similar experience:
- treat unikernel builds as first-class artifact targets
- keep configuration as typed inputs
- ensure the resulting image has a contract surface we can diff/review

### 4) Userspace kernel components for testing and tooling

Rump kernels are strong prior art for:
- mounting/manipulating filesystem images without host mount privileges
- redirecting syscalls for unmodified tooling to a controlled kernel service

DeriveBSD can use this in the build/test pipeline:
- validate images and run FS checks inside jailed test harnesses
- reduce the need for privileged host mounts in CI

See also: `docs/355-rump-kernels-and-userspace-driver-testing.md`.

## DeriveBSD mapping (proposal)

### Artifact target type (optional)

Add an artifact target type:
- `unikernel-image`
  - store object: the payload image bytes
  - manifest declares: expected ABI, required devices, allowed channels

Launch-time policy either:
- runs it under an approved wrapper, or
- refuses if the host lacks an approved wrapper.

### Evidence hooks

Emit evidence objects when this lane is used:
- `runtime.contract.json` (declared resources)
- `launch.policy.trace.json` (why it was allowed)
- `wrapper.identity.json` (version/digest of the execution wrapper)

### Safety posture

Defaults:
- off unless explicitly requested
- network and IO are denied unless declared
- debug channels are separate and policy-gated

Last updated: 2026-02-27r107
