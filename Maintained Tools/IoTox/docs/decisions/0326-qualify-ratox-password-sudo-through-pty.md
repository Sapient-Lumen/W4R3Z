# ADR 0326: Qualify Ratox password sudo through the production PTY

- Status: accepted and implemented
- Date: 2026-09-03

## Context

ADR 0286 made privilege gain explicit and default-off. Its NixOS VM proved that an approved
compatibility profile could cross the production PTY into a real set-ID-root `sudo` child, but the
fixture deliberately used passwordless policy. That established kernel and profile behavior without
establishing the human interaction IoTox's intended owner-admin shell normally needs: a terminal
prompt, disabled echo, PAM verification, and continuation in the same non-root login shell.

A password-prompt gate must not discard the simpler noninteractive branch. The two paths catch
different regressions, and one synthetic password policy is not evidence for every host's PAM,
sudoers, hardware-token, or graphical conversation stack.

## Decision

Extend `ratox-sudo-vm` to create two disjoint fixture accounts. `operator-nopasswd` retains a
dedicated test-only NOPASSWD rule and the existing exact set-ID branch. The real `operator` remains
in `wheel`, starts as UID/GID 1000 with the reviewed `--allow-sudo` shell profile, and must satisfy
the VM's password-requiring sudo policy.

The production PTY test starts immutable Nix-store Bash as the operator login shell, prints its
pre-sudo effective UID, submits `sudo -k` with a unique prompt, waits until that prompt has crossed
the controller stream, sends the synthetic password as terminal input, and runs `id -u` in the sudo
child. It requires UID 0 only in that child, exit 0, UID 1000 after sudo returns, clean shell exit,
and absence of the password from all captured terminal output.

The shell executable must be its canonical immutable Nix-store path. The first attempted fixture
used `/run/current-system/sw/bin/bash`; IoTox correctly refused the symlinked path during
descriptor-pinned executable resolution, so it did not count as a sudo attempt.

## Consequences

The x86_64 NixOS VM on Linux 6.6.94 passed both the noninteractive and password-prompt paths. This
closes the first real PAM/password sudo conversation through IoTox's local production PTY boundary
and strengthens the daily-control case without changing Ratox v1 framing, remote authority, profile
selection, or privilege defaults.

It does not traverse the Tox transport in this check, qualify password retries/timeouts, support
arbitrary PAM conversation plugins, prove FIDO/U2F/smartcard behavior, validate a user's actual
sudoers policy, protect a compromised live terminal, or activate Ratox by default. The remote
principal bound to an admin profile still has the practical power of that sudo-capable login.
