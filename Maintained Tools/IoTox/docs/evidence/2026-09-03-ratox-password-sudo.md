# Ratox password-prompt sudo qualification

- Date: 2026-09-03
- Host: IoTox founding x86_64 machine
- Decision: ADR 0326
- Status: NixOS KVM gate accepted

## Direct gate

```sh
nix build .#checks.x86_64-linux.ratox-sudo-vm -L
```

The accepted output is
`/nix/store/4i7hgbzc8x8qb0s462llm7zk4ri9wh8j-vm-test-run-iotox-ratox-sudo`.
The source-linked harness IoTox SHA-256 is
`92015fdae830b84fd697c2cfc18fbf68f9c2cadfce2e3a9fafcfae62a2a900bf`; the production PTY test
driver SHA-256 is
`4131c45b764846b48c69f713194613685fb31efd3039b749e4403e07922ee583`.

One x86_64 KVM guest booted NixOS on Linux 6.6.94. It verified deterministic shell and sudo
discovery, generated the disabled owner-admin profile, and required exact UID/GID 1000,
`confinement=compatibility`, and `allow-privilege-escalation=1`.

Two production-PTY branches then passed:

- UID 1001 used one test-only NOPASSWD rule, reached UID 0 only in the `sudo --non-interactive`
  child, and returned to UID 1001.
- UID 1000 started canonical Nix-store Bash, reached the unique `IOTOX-SUDO-PASSWORD:` prompt,
  submitted the synthetic VM password with terminal echo disabled, reached UID 0 only in the sudo
  child after PAM acceptance, returned to UID 1000, and exited cleanly. The captured terminal byte
  stream did not contain the password.

The final VM script completed in 12.97 seconds. A preceding rejected attempt passed a symlinked
`/run/current-system/sw/bin/bash`; descriptor-pinned spawn refused it with `Not a directory` before
sudo or PAM. The accepted retry used the canonical immutable store path.

## Evidence boundary

The synthetic password appears only as test-fixture input and is not an operator secret. This gate
crosses IoTox's real PTY/process boundary and the guest's real set-ID sudo/PAM policy, but not Tox or
a remote controller. It does not qualify all PAM modules, multiple failed attempts, timeout/lockout,
hardware tokens, password-change conversations, host-specific sudoers, or production activation.
