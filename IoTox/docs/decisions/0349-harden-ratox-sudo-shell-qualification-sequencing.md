# ADR 0349: Harden Ratox sudo-shell qualification sequencing

Status: accepted. Implemented 2026-09-09.

## Context

The full flake gate exposed a timing-sensitive failure in `ratox-sudo-vm`: the VM's password sudo
command succeeded, PAM opened and closed the root session, but the test harness timed out waiting
for the enclosing Bash login shell to exit.

That is the exact owner-control path IoTox cares about for SSH-like administration:

- start a non-root owner-approved login shell;
- type a real sudo password through the PTY with echo disabled;
- run one root child;
- return to the same non-root shell; and
- continue issuing ordinary shell input.

The product boundary was already correct. The weak point was the qualification harness sending its
post-sudo status/exit continuation immediately after observing the UID-0 output. On the NixOS VM,
that can race the shell regaining terminal control after sudo restores terminal mode and PAM closes
its session.

## Decision

Make the password-sudo shell qualification behave more like an interactive terminal session:

- set a deterministic prompt and clear `PROMPT_COMMAND` inside the test shell;
- after observing the UID-0 sudo child output, wait briefly for sudo/PAM terminal cleanup before
  sending the next shell command;
- prefix the continuation with a newline so an unterminated prompt repaint cannot fuse with the
  status command; and
- include bounded phase/output-tail diagnostics when `collect_to_exit()` times out.

This is a test-harness hardening change only. It does not change Ratox framing, remote authority,
profile selection, privilege defaults, sudo discovery, PAM policy, or compatibility confinement.

## Consequences

The isolated VM sudo gate now better represents the intended SSH-like operation model: a real human
or terminal client waits for the shell to return before submitting the next privileged workflow
step. Future failures identify whether the controller is still running, whether output is closed,
and the tail of the PTY stream rather than reporting only a generic timeout.

This remains one NixOS sudo/PAM policy. It does not prove hardware-token prompts, graphical
conversation helpers, every sudoers configuration, remote Tox traversal, or production activation.

## Evidence

Accepted local checks:

```text
nix develop -c bash -lc 'cmake --build build -j2 --target iotox_terminal_posix_process_tests && ctest --test-dir build -R "terminal-posix-process" --output-on-failure'
nix build .#checks.x86_64-linux.ratox-sudo-vm --no-link -L
```
