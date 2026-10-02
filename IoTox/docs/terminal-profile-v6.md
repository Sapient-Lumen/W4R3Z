# IoTox local terminal profile v6

> Historical compatibility format. The encoder now emits `iotox-terminal-profile-v7`; canonical v6
> records remain accepted without executable byte pins. See `terminal-profile-v7.md` for the current
> payload-integrity boundary.

Status: introduced in rev0046; historical compatibility format as of 2026-09-02
Wire effect: none; profiles are owner-local policy and Ratox v1 framing is unchanged
Superseded by: terminal profile v7; exact canonical v1--v5 records also remain accepted

## Purpose

Profile v6 keeps every v5 executable, environment, dimensions, rlimit, cgroup, shutdown, and
confinement rule. It adds the missing owner-workstation boundary:

- a frozen login-account identity with exact supplementary groups; and
- an explicit, default-false permission for later host-authorized privilege gain.

The remote peer still supplies only terminal input and resize/control records after the owner-bound
profile has been resolved. It cannot select a path, argv, environment, UID, group, confinement tier,
or elevation policy.

## Canonical record

The record is LF-terminated, field-ordered, and byte canonical. Integers are unsigned decimal with no
redundant leading zero. Hex is lowercase and even length. Repeated inherited/fixed environment and
supplementary-group entries are sorted. Decoding succeeds only when encoding the parsed value under
the same historical version reproduces every input byte.

```text
iotox-terminal-profile-v6
id=<profile-id>
enabled=<0|1>
argument-hex=<hex bytes>                 repeated 1..32
working-directory-hex=<hex bytes>
terminal-type=<token>
inherit-environment=<name>               repeated, sorted
environment-hex=<name>:<hex value>       repeated, sorted by name
identity=inherit
    OR
identity=exact:<uid>:<gid>:1
    OR
identity=account:<uid>:<gid>
supplementary-group=<gid>                 account only, repeated 0..256, sorted unique, excluding primary gid
confinement=compatibility|baseline|strict
allow-privilege-escalation=<0|1>
cgroup-pids-max=none|<u64>
cgroup-memory-high-bytes=none|<u64>
cgroup-memory-max-bytes=none|<u64>
cgroup-swap-max-bytes=none|<u64>
cgroup-cpu-quota-us=none|<u64>
cgroup-cpu-period-us=none|<u64>
cgroup-io-device=none|<canonical-u32>:<canonical-u32>
cgroup-io-rbps=none|<u64>
cgroup-io-wbps=none|<u64>
cgroup-io-riops=none|<u64>
cgroup-io-wiops=none|<u64>
minimum-dimensions=<columns>:<rows>
initial-dimensions=<columns>:<rows>
maximum-dimensions=<columns>:<rows>
allow-resize=<0|1>
limit-cpu-seconds=<u64>
limit-address-space-bytes=<u64>
limit-file-size-bytes=<u64>
limit-open-files=<u64>
limit-processes=<u64>
hangup-grace-ms=<u64>
terminate-grace-ms=<u64>
kill-reap-grace-ms=<u64>
```

All v5 cgroup I/O composition, enforcement, and teardown-accounting semantics remain unchanged; see
`terminal-profile-v5.md`. Profile v6 changes no cgroup kernel interface.

## Identity modes

`identity=inherit` retains the Agent identity and current supplementary groups. In-memory UID/GID
fields must be zero and the supplementary vector empty. It is unsuitable for a root Agent serving a
non-root owner shell.

`identity=exact:<uid>:<gid>:1` clears all supplementary groups and converges real, effective, and
saved IDs exactly. It remains the isolation-oriented mode required by delegated cgroup profiles.

`identity=account:<uid>:<gid>` restores the listed numeric supplementary-group set. The primary GID
is represented only by the identity field and is excluded from that supplementary vector. If the Agent is
already that account, all six IDs and the complete current group set must match. Otherwise the Agent
must possess authority to call `setgroups`, `setresgid`, and `setresuid`; after transition the child
verifies every ID and group. A mismatch or unavailable transition fails before target exec.

Account membership is deliberately frozen. Profile execution does not perform an NSS lookup and a
later `/etc/group` change does not silently widen an installed profile. Regenerate the profile to
adopt a membership change.

An account identity owned by the same daemon UID must use `limit-processes=0`, for the same reason as
inherit mode: `RLIMIT_NPROC` counts the whole real UID rather than one PTY. A delegated cgroup
`pids.max` is unavailable to the compatibility sudo profile and exact dedicated identities remain
required for isolated cgroup sessions.

## Default and sudo-capable boundaries

`allow-privilege-escalation=0` is the ordinary contract. The child sets and verifies
`PR_SET_NO_NEW_PRIVS=1`, clears ambient/active capabilities, seals privileged securebits and the
bounding set where it has the authority to do so, and then applies baseline or strict confinement.
Set-ID and file-capability executables cannot gain privilege.

`allow-privilege-escalation=1` requires compatibility confinement and a non-root starting identity.
At spawn the child requires inherited `no_new_privs=0`, unrestrictive root/setuid securebits, and
`CAP_SETUID`/`CAP_SETGID` in the capability bounding set. It clears every ambient, effective,
permitted, and inheritable capability but preserves the ordinary bounding set and root semantics for
a later host-authorized set-ID/file-capability helper.

This mode is not merely a sudo allowlist. It permits any helper the local filesystem and account can
execute to apply its normal kernel privilege semantics. The `--allow-sudo` authoring ceremony checks
that a privileged sudo executable exists, but sudoers/PAM/password policy remains entirely host
owned and is reported as `not-probed`.

Because a successful sudo child is root, baseline seccomp, strict Landlock/MDWE, delegated cgroup
containment, and their sandbox claims are unavailable. Compatibility still fixes the target and
environment, closes descriptors, disables core dumps, applies rlimits, owns the PTY/process group,
and clears active capabilities before exec. It does not claim to contain the owner after sudo.

## Owner-shell authoring

Inspect what the host will use:

```bash
iotox terminal-shell-discover
iotox terminal-shell-discover USER
iotox --shell /absolute/reviewed/shell terminal-shell-discover USER
```

Candidate order is explicit override, passwd shell, current `$SHELL` for the current account, then
bounded `bash`/`zsh`/`fish`/`ksh`/`oksh`/`mksh`/`dash`/`ash`/`sh`/`csh`/`tcsh` names across the
deterministic NixOS/conventional PATH. Candidates resolve symlinks to one normalized absolute path and
must be regular ELF executables, have an execute bit, have no set-ID bit, not be group/other writable,
be executable by the target identity, and be owned by root, the Agent UID, or the frozen account UID.
An explicit bad path is an error, not permission to fall back.

Generate one of two disabled profiles:

```bash
# Ordinary login shell: baseline confinement, privilege gain denied.
iotox terminal-profile-shell-template owner-shell > owner-shell.profile

# Full host administration: non-root login plus explicit host-authorized sudo.
iotox --allow-sudo terminal-profile-shell-template owner-admin \
  > owner-admin.profile
```

`--shell PATH` and optional `USER` may be supplied to either template. The template freezes
`HOME`, `LOGNAME`, `USER`, `SHELL`, and this deterministic PATH order when applicable:

```text
/etc/profiles/per-user/USER/bin
HOME/.local/bin
HOME/.nix-profile/bin
/run/wrappers/bin
/run/current-system/sw/bin
/nix/var/nix/profiles/default/bin
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

Only `LANG` and `TZ` are inherited. The selected canonical shell is argv[0]; known interactive
shells receive fixed `-l`. Unknown explicit ELF programs receive no invented argument.

### Optional static rescue entrance

When the host login shell or its dynamic userland may be unavailable, build the separately pinned
rescue payload and qualify it for the same account:

```bash
nix build .#iotox-rescue-toolbox
iotox --shell "$PWD/result/bin/oksh" --toolbox-dir "$PWD/result/bin" \
  terminal-shell-discover "$USER"
iotox --shell "$PWD/result/bin/oksh" --toolbox-dir "$PWD/result/bin" \
  terminal-profile-toolbox-template owner-rescue "$USER" \
  > owner-rescue.profile
```

This disabled profile uses canonical profile v6 without adding fields or changing Ratox. It starts
the exact static oksh with `-i`, prefixes the deterministic PATH with the qualified Toybox directory,
fixes history to `/dev/null`, and retains baseline/default-denied privilege policy. It deliberately
does not set `ENV`: that remains a prohibited startup-code hook, and the child environment is already
exact rather than ambient. `--allow-sudo` may create a separate rescue-admin compatibility profile
under the same host-policy limits described below; the toolbox itself contains no sudo.

See `ratox-rescue-toolbox.md` and ADR 0287 for contents, qualification, licensing, retention, and
failure limits. The real account login shell remains the preferred primary profile.

Review the complete file, change `enabled=0` to `enabled=1`, then use the ordinary strict store
commands:

```bash
iotox terminal-profile-lint owner-admin.profile
iotox --ratox-profile-store /var/lib/iotox/ratox \
  terminal-profile-install owner-admin.profile
iotox --ratox-profile-store /var/lib/iotox/ratox \
  terminal-profile-bind PRINCIPAL_PUBLIC_KEY_HEX owner-admin
```

The Agent loads the store only at activation. Existing sessions retain the prior immutable profile
generation. On NixOS the canonical shell may be a `/nix/store` path; after a system upgrade, rerun
discovery and reinstall instead of silently following a changed symlink.

## Password and authority boundary

If sudo prompts, the password is terminal input protected by the established Tox/Ratox channel. IoTox
does not place terminal contents in its status or lifecycle journals. The remote endpoint and local
PTY necessarily see those bytes, so a compromised authorized client/session has the same power as a
compromised interactive login. Prefer narrowly scoped sudoers rules where full root is unnecessary.

The generated profile does not modify sudoers, install a passwordless rule, cache credentials, test a
password, or claim authorization. `terminal-shell-discover` and `host-capabilities` report only the
observed executable mechanism and `sudo-policy=not-probed`.

## Compatibility

The decoder accepts canonical v1 through v6. Historical fields retain their original meanings:

- v1 maps to compatibility and has no cgroup policy;
- v2 adds confinement;
- v3 adds process/memory/swap/CPU cgroup fields;
- v4 adds `memory.high`;
- v5 adds exact-device I/O policy; and
- v1--v5 synthesize no account groups and `allow-privilege-escalation=false`.

Re-encoding any accepted historical record emits v6. No historical record is reinterpreted as
sudo-capable.
