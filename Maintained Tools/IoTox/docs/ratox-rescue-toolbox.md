# Ratox rescue toolbox

Status: x86_64-linux production-PTY qualified; AArch64 passes qemu-user and a system-emulated
AArch64-kernel production PTY, with one named real target still required; default off; updated
2026-09-02.

The normal IoTox shell is the account's real login shell. Keep that as the primary profile: it knows
the machine, its startup conventions, package environment, and administrator workflow. The rescue
toolbox is a second owner-installed profile for a narrower failure: IoTox, the kernel, PTYs, storage,
and networking still work, but the ordinary shell, dynamic loader, shared libraries, or basic command
set cannot be trusted to be present.

Ordinary discovery is itself broad but bounded: after the explicit/passwd/current-environment
candidates it searches eleven known shell names across the deterministic per-user, NixOS, and
conventional PATH. Every result still resolves to one qualified ELF. The static rescue profile exists
for the case where none of those host-userland choices is dependable.

## What is in it

`nix build .#iotox-rescue-toolbox` and `nix build .#iotox-rescue-toolbox-aarch64` each construct two
statically linked ELF files from the same pinned sources:

| Architecture | oksh 7.9 | Toybox 0.8.14 | Total raw ELF |
|---|---:|---:|---:|
| x86_64-linux | 398,200 bytes | 876,648 bytes | 1,274,848 bytes |
| aarch64-linux | 459,848 bytes | 974,272 bytes | 1,434,120 bytes |

Each package exposes 240 names in total (`oksh`, `toybox`, and 238 applet aliases). It deliberately
does not expose `sh` or `toysh`: Toybox upstream still describes that shell as partially implemented.
Each package carries `share/iotox-rescue/manifest`, a validated SPDX 2.3 tag-value document, exact
payload SHA-256 digests, source provenance, and the applicable notice files. oksh's optional
curses screen-clear integration is disabled: otherwise the static ELF embeds its build-time Nix
terminfo path. The build rejects an interpreter, a dynamic dependency, or any embedded `/nix/store/`
string in either ELF; ordinary Emacs/vi line editing remains compiled in.

This package is not embedded in or linked to `iotox`. It is an optional deployment payload, so an
operator can omit it completely, preserve it in a Nix generation, or copy the two resolved static
executables and notices to a reviewed immutable location appropriate for another image system.

## Build, inspect, and author

```bash
nix build .#iotox-rescue-toolbox
nix build .#iotox-rescue-toolbox-aarch64

IOTOX_RESCUE="$PWD/result/bin"
iotox --shell "$IOTOX_RESCUE/oksh" --toolbox-dir "$IOTOX_RESCUE" \
  terminal-shell-discover "$USER"

iotox --shell "$IOTOX_RESCUE/oksh" --toolbox-dir "$IOTOX_RESCUE" \
  terminal-profile-toolbox-template owner-rescue "$USER" \
  > owner-rescue.profile

iotox terminal-profile-lint owner-rescue.profile
```

The generated profile is intentionally `enabled=0`. Review its canonical shell, account IDs,
supplementary groups, arguments, PATH, and confinement; change it to `enabled=1`; lint again; then
install and bind through the ordinary profile-store commands documented in
`terminal-profile-v7.md`. The generated v7 profile contains the exact SHA-256 pins of `oksh` and
`toybox`; runtime rehashes those descriptor-pinned payloads immediately before process creation.

The default rescue profile is non-root and cannot gain privilege. If this principal truly needs full
host administration, create a visibly separate profile:

```bash
iotox --shell "$IOTOX_RESCUE/oksh" --toolbox-dir "$IOTOX_RESCUE" \
  --allow-sudo terminal-profile-toolbox-template owner-rescue-admin "$USER" \
  > owner-rescue-admin.profile
```

That flag does not add sudo to the bundle. It only permits the shell to invoke a qualified sudo found
later in the deterministic host PATH, subject to the machine's existing sudoers/PAM policy. Keep a
baseline rescue binding whenever root is unnecessary.

## Resolution and environment contract

IoTox canonicalizes the shell and toolbox directory before encoding a profile. Every toolbox path
component must have trusted ownership, be searchable by the account, and resist other-user
replacement (ordinary group/world-writable parents fail; sticky directories are allowed). The final
directory and Toybox executable must pass owner/mode/ELF checks and be executable by the selected
non-root account.
The fixed PATH is:

```text
QUALIFIED_TOOLBOX
/etc/profiles/per-user/USER/bin
HOME/.local/bin
HOME/.nix-profile/bin
/run/wrappers/bin
/run/current-system/sw/bin
/nix/var/nix/profiles/default/bin
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

The shell starts with fixed `-i`, not `-l`, so a damaged host login-profile chain is not a rescue
prerequisite. The environment is exact: `HOME`, `LOGNAME`, `USER`, `SHELL`, `PATH`,
`HISTFILE=/dev/null`, `PS1`, and `IOTOX_RESCUE_TOOLBOX`, plus terminal type and optionally inherited
`LANG`/`TZ`. Hazardous startup variables such as `ENV`, `BASH_ENV`, and loader variables are absent.

## What this can and cannot rescue

It can buy an operator a predictable shell and tools such as `cat`, `cp`, `dd`, `df`, `dmesg`, `find`,
`grep`, `id`, `ifconfig`, `ls`, `mount`, `netcat`, `ps`, `sed`, `sha256sum`, `tar`, `top`, and `xxd`
without the target's dynamic libraries. Exact included applets are the output of
`result/bin/toybox`; absent commands are not implied by the category “toolbox.”

It cannot help if IoTox is not running/reachable, the authority/profile store was not prepared, the
kernel cannot execute this architecture/ABI, the PTY or filesystem is unusable, or the storage
containing the rescue payload was collected/corrupted. It is not an initramfs, a boot loader, a
second daemon, a sandbox, a backup, or automatic failover. Install and qualify it before needing it.

## AArch64 kernel boundary and remaining real-target gate

ADR 0301 completes the architecture-neutral construction half of roadmap workstream 9. The AArch64
package passes the same source, license, static-ELF, no-interpreter, no-`DT_NEEDED`, no-store-reference,
applet-inventory, manifest, SPDX, and provenance gates as x86_64. qemu-user executes oksh and two
distinct Toybox applets. An x86_64-kernel Sandwurm VM also proves binfmt registration, non-root direct
execution, and IoTox discovery of the exact AArch64 capsule.

The production PTY intentionally does not pass through x86-kernel binfmt: IoTox launches the already-reviewed
close-on-exec executable descriptor with `fexecve`, while Linux binfmt must hand that descriptor to an
interpreter after exec. The retained VM test requires the resulting final-stage `ENOENT`; opening a
path again or weakening descriptor closure would turn an emulator convenience into a real replacement
race. This is useful negative evidence, not native-AArch64 qualification.

ADR 0304 adds the corresponding positive system gate. A minimal QEMU `virt` guest boots locked
AArch64 Linux 6.6.94, creates an ordinary UID/GID 1000 account, and runs the unchanged production
qualifier. Profile-v7 descriptor pins, oksh PTY start, capsule-only command discovery, identity,
file/hash/list work, and clean exit pass. This is an actual AArch64 kernel under TCG, not an
x86-kernel binfmt shortcut.

Acceptance therefore now requires only one named real device ABI/kernel gate. Later constrained
Linux targets are selected only if they can satisfy the same contract. QEMU evidence does not imply
board firmware, image, physical-storage, performance, or deployment reliability. Capsules remain
opt-in files selected by an owner-approved profile. IoTox never downloads or executes a peer-supplied
toolbox automatically.
Exact current bytes and commands are retained in
`evidence/2026-09-02-aarch64-rescue-capsule.md`.
