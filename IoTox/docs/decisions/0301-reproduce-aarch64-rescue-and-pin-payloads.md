# ADR 0301: Reproduce the AArch64 rescue capsule and pin payload bytes

- Status: accepted and implemented; AArch64-kernel follow-on completed by ADR 0304
- Date: 2026-09-02

## Context

ADR 0287 shipped one small static x86_64 rescue toolbox, but profile v6 bound only paths. Roadmap
workstream 9 required an AArch64 reproduction, exact payload digests in reviewed profiles,
machine-readable provenance, and a production PTY proof on each recommended architecture.

Cross-compilation and emulation answer different questions. A user-mode emulator can prove the ELF
and basic syscall ABI while missing the target kernel, boot chain, seccomp audit architecture, PTY,
and IoTox descriptor handoff. Treating those as equivalent would erase the most important remaining
deployment boundary.

## Decision

Add `.#iotox-rescue-toolbox-aarch64`. It builds pinned oksh 7.9 and Toybox 0.8.14 with the same
no-curses patch and the same 238-applet inventory as x86_64. Construction rejects a non-AArch64
ELF, interpreter, `DT_NEEDED`, embedded `/nix/store/`, missing notices, or inventory drift. Both
architectures now append exact ELF SHA-256 values to the manifest and carry an SPDX 2.3 tag-value
document that is validated during the build with `pyspdxtools`.

Add profile v7. Shell and toolbox templates compute exact SHA-256 pins; the PTY parent hashes the
already-open target descriptor and refuses a mismatch before spawn. The rescue companion is the
exact regular `IOTOX_RESCUE_TOOLBOX/toybox` payload. Canonical v1--v6 records remain readable and
unpinned.

The host-achievable ARM gates are deliberately split:

1. `ratox-rescue-toolbox-aarch64-user` runs oksh, Toybox `printf`, and Toybox `sha256sum` under
   `qemu-aarch64`.
2. `ratox-rescue-toolbox-aarch64-binfmt-vm` boots an x86_64 NixOS VM, registers the AArch64
   `binfmt_misc` handler, proves ordinary non-root execution and IoTox discovery, then requires the
   production PTY to refuse at final descriptor-based `fexecve` with `ENOENT`.

IoTox will not clear the close-on-exec descriptor or add an emulator wrapper merely to turn that
negative result green. Doing so would weaken the native descriptor-hygiene contract and still would
not create an AArch64 kernel.

## Consequences

The same independently versioned payload is reproducible for the two dominant Linux CPU ABIs, and
reviewed profiles now make executable replacement visible at launch. The AArch64 capsule is useful
for image construction and has real user-ABI evidence.

The pin is not filesystem immutability or local-root resistance. Production capsule deployment must
retain the payload on reviewed immutable or verified storage; a trusted local owner can otherwise
mutate an inode, including in the narrow interval after hashing and before exec.

At this decision boundary it was not yet recommended as a qualified Ratox rescue entrance on
AArch64. That required the
unchanged production PTY suite under an AArch64 kernel in QEMU system emulation or real target
hardware; ADR 0304 subsequently passes that system-emulation gate. At least one named target
ABI/kernel gate still remains. The x86_64 production-PTY claim remains qualified. No Ratox or local
terminal framing changed.
