# ADR 0287: ship an explicit static rescue toolbox

Status: accepted, 2026-09-01.

## Context

ADR 0286 makes a real account login shell the normal Ratox entrance. That is the best operator
experience when the machine's userland is healthy, but it leaves a recovery dependency on the
selected shell, its dynamic loader and libraries, and the ordinary utilities reachable through the
host PATH. A damaged upgrade, incomplete image, or deliberately tiny appliance may retain a working
Linux kernel and IoTox while losing one of those pieces.

BusyBox is the best-known mature single-binary rescue environment, but its GPL-2.0-only distribution
terms would add another copyleft component to this optional payload. Toybox is small, broadly useful,
0BSD-licensed, and already used as Android's command-line toolbox. Its own `sh`/`toysh` implementation
is nevertheless still classified upstream as partially implemented. A rescue entrance must not make
an interactive shell promise on pending code.

## Decision

IoTox provides a separate `iotox-rescue-toolbox` Nix package for `x86_64-linux`. It contains:

- a statically linked oksh 7.9 executable as the interactive shell;
- a statically linked Toybox 0.8.14 multicall executable and 238 utility aliases; and
- source/version/hash provenance plus Toybox and oksh notices.

The two ELF payloads total approximately 1.22 MiB in the current build. `sh` and `toysh` aliases are
absent and the package build fails if the selected Toybox configuration exposes either name. The
exact upstream archives are SHA-256 pinned. A separately locked Nixpkgs toolchain builds this optional
static payload without changing the product, deployment-VM, or source-linked IoTox package universe.
oksh is built with its supported curses integration disabled and a three-guard correction retained
locally for that upstream mode: curses otherwise embeds an absolute build-time terminfo path. Both
ELFs must contain no interpreter, dynamic dependency, or `/nix/store/` string.

This remains one IoTox product executable. oksh and Toybox are third-party deployment payloads, not
new IoTox implementations, not linked into `iotox`, and not included in the core six-component
source SBOM. A deployment that distributes the rescue package must carry its separate notices and
inventory.

Two owner-local surfaces make the choice explicit:

```text
iotox [--shell PATH] [--toolbox-dir PATH] terminal-shell-discover [USER]
iotox --shell PATH --toolbox-dir PATH [--allow-sudo] \
  terminal-profile-toolbox-template PROFILE_ID [USER]
```

The toolbox directory must resolve to an absolute normalized directory owned by root, the Agent, or
the target account and must not be group/other writable. Every path component must have the same
trusted ownership, be searchable by the target account, and must not be group/other writable unless
it has sticky-directory semantics (for example `/tmp`). Its `toybox` entry must resolve through the
same regular-ELF, ownership, mode, set-ID, and target-executability checks as a shell. The explicit
shell is independently canonicalized by those checks. Invalid explicit input fails; IoTox never
silently substitutes the rescue entrance.

The emitted canonical profile-v6 record is disabled. It starts the fixed shell with `-i`, freezes the
real non-root account and groups, and places the qualified toolbox directory before the normal
deterministic host PATH. It fixes `HISTFILE=/dev/null`, a rescue prompt, and a content-free
`IOTOX_RESCUE_TOOLBOX` marker. `ENV` remains absent because IoTox classifies it as a hazardous shell
startup hook; the child receives an exact sealed environment rather than ambient process variables.
Only `LANG` and `TZ` may be inherited.

Privilege escalation is denied under baseline confinement by default. `--allow-sudo` is the same
separate, visible compatibility decision as ADR 0286: it requires a host privileged sudo helper and
does not grant or inspect sudoers/PAM authority. The toolbox itself carries no sudo implementation.

## Qualification

Owned CLI tests prove exact toolbox/shell selection, canonical profile arguments and environment,
default-denied privilege gain, and rejection of a group-writable toolbox or non-sticky writable
parent component.

The production PTY qualification runs as a real non-root account with PATH restricted to the bundle.
Across the ordinary baseline process boundary it starts interactive oksh, locates Toybox and `id`,
observes the non-root identity, creates a file, hashes it with the expected SHA-256, lists it, and exits
cleanly. The `ratox-rescue-toolbox-vm` flake check repeats discovery, profile generation, and that
production PTY proof inside an isolated NixOS VM.

## Consequences

The ordinary login shell remains preferred. The rescue profile is a preinstalled, separately bound
fallback for cases where enough of Linux and the IoTox executable still work but ordinary userland
does not. Static linking removes the target's dynamic-loader/library dependency; it does not remove
the CPU architecture, Linux syscall ABI, filesystem, PTY, kernel confinement, Tox reachability,
authority, installed-profile, or Agent-liveness dependencies.

The leading toolbox PATH makes ordinary names deterministic but is not a containment mechanism. An
interactive owner shell can still invoke an absolute host path, and a sudo-capable profile can become
root under host policy. Exact Nix store paths may disappear after garbage collection; operators must
retain the rescue payload or copy it into an immutable reviewed deployment location, then regenerate
and reinstall profiles deliberately when the payload changes.
