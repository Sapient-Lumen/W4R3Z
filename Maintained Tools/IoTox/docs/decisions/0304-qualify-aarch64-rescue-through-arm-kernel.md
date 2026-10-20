# ADR 0304: Qualify the AArch64 rescue capsule through an ARM kernel

- Status: accepted and implemented for system-emulated AArch64 Linux; named real-target qualification remains open
- Date: 2026-09-02

## Context

ADR 0301 reproduced the pinned rescue payloads for AArch64 and ran them under qemu-user. Its retained
x86-kernel binfmt gate correctly stopped at IoTox's descriptor-only `fexecve` boundary: the kernel's
binfmt interpreter could not reopen the close-on-exec executable descriptor. That was useful negative
evidence, but it did not exercise the AArch64 kernel exec, PTY, seccomp-audit-architecture, or process
identity path.

The next host-achievable gate had to preserve the production descriptor contract. Adding a pathname
fallback or emulator wrapper would test a different and weaker design.

## Decision

Add `checks.x86_64-linux.ratox-rescue-toolbox-aarch64-system-vm`. The derivation boots the locked
NixOS AArch64 Linux 6.6.94 kernel under QEMU `virt`/TCG with a deliberately minimal test initramfs.
The initramfs contains static Busybox only for boot plumbing, the complete runtime closure of the
cross-built current IoTox terminal-process harness, and the independently pinned AArch64 oksh/Toybox
capsule.

The guest creates an ordinary UID/GID 1000 account, mounts devtmpfs and devpts, and invokes the
unchanged rescue qualifier as that non-root user. The qualifier:

- hashes the exact oksh and Toybox descriptors and applies profile-v7 pins;
- starts oksh through the production `PosixPtyProcessFactory` and sealed `fexecve` handoff;
- keeps the baseline confinement and no-privilege-escalation profile;
- proves the shell and `toybox`/`id` applet resolution with no host tools in `PATH`;
- checks the non-root identity, creates a file, hashes it, lists it, and exits normally.

The host requires the exact `aarch64` kernel marker, qualifier-success marker, and guest completion
marker. Serial CRLF is normalized only in the host transcript before exact marker comparison; guest
execution and PTY bytes are unchanged.

## Consequences

The AArch64 capsule now has construction-host evidence through an actual AArch64 kernel and the
unchanged production PTY boundary. The qemu-user positive gate and x86-kernel binfmt negative gate
remain because they isolate distinct layers and make regressions legible.

QEMU TCG is not physical ARM hardware, firmware, storage, a device image, performance evidence, or a
deployment recommendation. Workstream 9 still requires one named real device ABI/kernel gate before
the capsule is recommended for that target. The test initramfs is a fixture, not an IoTox rescue
image or a new product artifact. No Ratox framing, profile semantics, or descriptor hygiene changed.
