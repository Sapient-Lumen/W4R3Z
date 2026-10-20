# AArch64 rescue-capsule construction evidence

Date: 2026-09-02  
Host: founding x86_64-linux machine  
Decisions: ADRs 0301 and 0304

## Reproducible payload

```bash
nix build .#iotox-rescue-toolbox .#iotox-rescue-toolbox-aarch64 --no-link -L
nix build .#checks.x86_64-linux.ratox-rescue-toolbox-aarch64-user --no-link -L
```

Both builds passed. Each package contains two static, interpreter-free, dependency-free ELFs,
238 Toybox applets, source provenance, notices, exact payload hashes, and an SPDX 2.3 document
validated by `pyspdxtools`.

| ABI | payload | bytes | SHA-256 |
|---|---|---:|---|
| x86_64-linux | oksh | 398,200 | `6143fb8102da06517e6c920db130a025f3d4cdc237996c10845f1fe01883f033` |
| x86_64-linux | toybox | 876,648 | `7bec9e1c24e204a52703000a48f7ef84749327d4d2ac0643fe303108777df40b` |
| aarch64-linux | oksh | 459,848 | `8a1e67c22d9e02c1e070e33706c66f5df2e34caa299d8df8e110b521bf0d0eff` |
| aarch64-linux | toybox | 974,272 | `1464fc88f57c5e2ac5f022b426c4073ec76460126b4ee984936e485647fa8cb4` |

Resolved packages occupy about 1.3 MiB and 1.4 MiB respectively. The QEMU user-mode check executed
the AArch64 shell and two distinct Toybox applets successfully.

## Kernel-binfmt boundary

```bash
nix build \
  .#checks.x86_64-linux.ratox-rescue-toolbox-aarch64-binfmt-vm \
  --no-link -L
```

The x86_64 NixOS VM registered `/proc/sys/fs/binfmt_misc/aarch64-linux`; an unprivileged account ran
the AArch64 oksh directly and IoTox accepted the shell/toolbox during discovery. The actual sealed
PTY path then stopped at:

```text
PTY child setup failed at final fexecve: No such file or directory
```

This is retained negative evidence. Linux user-mode binfmt cannot reopen the close-on-exec target
behind IoTox's descriptor-only `fexecve` contract. It proves neither a payload defect nor an AArch64
kernel pass. The check requires this exact refusal so a future behavioral change cannot silently
become an ARM qualification claim.

## AArch64-kernel production PTY

```bash
nix build \
  .#checks.x86_64-linux.ratox-rescue-toolbox-aarch64-system-vm \
  --no-link -L --max-jobs 1 --cores 2
```

The retained gate passed. It booted locked NixOS AArch64 Linux 6.6.94 under QEMU `virt`/TCG, mounted
the guest device and PTY filesystems, created UID/GID 1000, and ran the cross-built current terminal
process harness as that non-root account. The serial transcript contained:

```text
aarch64-kernel=aarch64
terminal rescue toolbox qualification passed
IOTOX-AARCH64-KERNEL-RESCUE-PASS
```

Behind the middle marker, profile-v7 hashes pinned the exact AArch64 oksh and Toybox files, the
production descriptor-only PTY path launched oksh, the shell resolved only capsule applets, `id`
reported the guest account, and file creation, SHA-256, listing, and clean exit all passed. An initial
wrapper run reached all three guest markers but exposed CRLF serial endings; the retained host gate
normalizes carriage returns before exact marker matching and then passed without changing guest
execution.

## Remaining acceptance

Repeat the same qualifier on one declared real target ABI/kernel. System emulation establishes the
AArch64 kernel/PTY/exec semantics used here, but does not establish board firmware, physical hardware,
storage, image integration, performance, or field reliability. Until a target is named and passes,
the capsule is construction-qualified rather than deployment-recommended.
