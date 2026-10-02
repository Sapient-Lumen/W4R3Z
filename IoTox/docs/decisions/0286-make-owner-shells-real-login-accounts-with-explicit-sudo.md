# ADR 0286: make owner shells real login accounts with explicit sudo

Status: accepted, 2026-09-01.

## Context

Ratox could already run a fixed owner-selected ELF executable, but its hardened child path always
armed `PR_SET_NO_NEW_PRIVS`, sealed securebits, and removed the capability bounding set. That is the
right default for appliance commands and deliberately makes set-ID/file-capability privilege gain
impossible. It also means an interactive shell cannot use ordinary `sudo`, regardless of sudoers
policy.

The existing exact identity mode clears every supplementary group. That is also correct for an
isolated payload, but it is not a faithful workstation login: an owner can lose `wheel`, storage,
virtualization, device, and project-group access. A non-root Agent cannot call `setgroups(2)` to
reconstruct those groups, so a superficially correct shell template could fail at process setup.

IoTox is intended to let its owner control their machine remotely. The primary experience therefore
needs a real login shell and ordinary host-governed sudo, while retaining a non-root, no-elevation
default and without adding a remote-selected command line.

## Decision

Canonical local terminal profiles advance to v6. The Ratox peer protocol, packet `0xA2`, local
terminal socket v1, authority capability, OPEN request, profile binding, and replay framing do not
change.

Profile v6 adds:

```text
identity=account:<uid>:<gid>
supplementary-group=<gid>          repeated 0..256, sorted and unique; primary gid excluded
allow-privilege-escalation=<0|1>
```

`identity=account` freezes the account's numeric primary and supplementary groups when the owner
authors the profile. A privileged Agent restores that exact set before dropping all real,
effective, and saved IDs. An Agent already running as that account verifies that its current six IDs
and group set match and performs no privileged identity mutation. NSS is consulted only by the
owner-local authoring command, never from remote input and never during profile decoding. Group
changes require a new reviewed profile.

`allow-privilege-escalation=0` is the universal default and the value synthesized for canonical
v1--v5 records. The historical child boundary remains: verified `no_new_privs`, capability hygiene,
and the selected baseline/strict confinement.

`allow-privilege-escalation=1` is deliberately broader than a sudo brand name: it permits later
host-authorized set-ID or file-capability execution. It is valid only when:

- the profile starts from a non-root identity;
- confinement is `compatibility`;
- no delegated cgroup session boundary is requested; and
- live inherited process state still has `no_new_privs=0`, ordinary securebits, and `CAP_SETUID` plus
  `CAP_SETGID` in the bounding set.

The child still clears ambient, effective, permitted, and inheritable capabilities before the shell
executes. It does not arm `no_new_privs`, lock out root semantics, or erase the bounding set. Calling
`sudo` later is therefore a new host authorization decision. IoTox neither edits sudoers nor treats a
present executable as proof that the account may elevate.

Baseline seccomp, strict Landlock/MDWE, and delegated cgroup containment are incompatible with a
general sudo-capable shell. A root process could need syscalls those policies deny and could undo
same-host containment; claiming those controls after granting full administration would be
misleading. The compatibility profile retains the PTY, fixed executable/environment, descriptor,
rlimit/core, parent-death, nondumpability setup, active-capability clearing, and process-group
lifecycle floor, but it is not a sandbox against the owner who becomes root.

Two owner-local commands author the intended path:

```text
iotox [--shell PATH] terminal-shell-discover [USER]
iotox [--shell PATH] [--allow-sudo] terminal-profile-shell-template PROFILE_ID [USER]
```

Discovery considers an explicit path, the account database shell, current `$SHELL` only for the
current account, and a bounded common-shell list. Every accepted shell is canonicalized to one
absolute regular ELF inode, executable by the target account, non-set-ID, not group/other writable,
and owned by root, the Agent, or the frozen account. An invalid explicit override fails instead of
silently falling back. The profile fixes `HOME`, `LOGNAME`, `USER`, `SHELL`, and a deterministic PATH
covering NixOS and conventional Unix locations; ambient development PATH content is never copied.

The template is always disabled. Without `--allow-sudo` it emits baseline/default-deny policy. With
the flag it also requires a discoverable setuid-root or file-capability sudo executable and emits the
explicit compatibility/elevation pair. Discovery reports `sudo-policy=not-probed` because presence
is not authorization.

## Qualification

The owned registry covers v1--v5 migration to v6, account-group canonicalization, default denial,
invalid confinement/root/group combinations, deterministic shell authoring, and explicit-override
failure. The native PTY process gate proves that default profiles retain `no_new_privs=1`, while the
explicit path starts non-root with the frozen groups, `no_new_privs=0`, zero active/ambient
capabilities, ordinary securebits, and a retained bounding set.

The `ratox-sudo-vm` flake check boots an isolated NixOS KVM guest, generates the real owner-admin
profile, and crosses the production IoTox PTY boundary with an actual setuid-root sudo child. ADR
0326 subsequently split the fixture accounts so the original deterministic noninteractive branch
remains while UID-1000 `operator` crosses the guest's password-requiring PAM policy through a real
login shell. Both require root only in the child and return to the original account; the password
branch additionally requires no password echo. This still does not qualify every host sudoers or
PAM policy.

## Consequences

An owner can bind a principal to a genuine login shell, type arbitrary shell commands interactively,
and use the machine's ordinary sudo policy. The remote still cannot choose a different executable,
argv, account, environment, profile, sudo rule, or privilege flag in OPEN bytes.

This is intentionally two profiles, not one ambiguous promise: use a baseline owner shell when
administration is unnecessary, and a separately reviewed `--allow-sudo` profile for the principal
that should possess full machine control. Compromise of that principal or live terminal is therefore
equivalent to compromise of the owner's sudo-capable login, subject to the host's own authentication
policy.

Exact canonical shell paths are immutable policy. On NixOS an upgrade or garbage collection can make
an old store path unavailable; the owner must rediscover, regenerate, review, reinstall, and restart
the Agent. IoTox does not silently retarget a profile to a newer shell.
