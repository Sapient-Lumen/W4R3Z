# IoTox local terminal profile v7

Status: canonical local encoder format as of 2026-09-02  
Wire effect: none; profiles are owner-local policy and Ratox v1 framing is unchanged  
Supersedes: v7 is emitted; exact canonical v1--v6 records remain accepted

## Purpose

Profile v7 retains every v6 identity, sudo, confinement, resource, environment, and lifecycle rule.
It adds byte identity for the executable selected by the owner and, for a rescue profile, the
Toybox multicall payload:

```text
iotox-terminal-profile-v7
id=<profile-id>
enabled=<0|1>
argument-hex=<hex bytes>                 repeated 1..32
executable-sha256=none|<64 lowercase hex>
toolbox-sha256=none|<64 lowercase hex>
working-directory-hex=<hex bytes>
...                                     unchanged canonical v6 fields
```

`toolbox-sha256` is valid only when `executable-sha256` is also present and one fixed
`IOTOX_RESCUE_TOOLBOX` environment entry names an absolute normalized directory. The pinned
companion is exactly `IOTOX_RESCUE_TOOLBOX/toybox`. A toolbox template now requires that final path
to be a regular non-symlink ELF; the applet symlinks may still point to that multicall binary.

## Enforcement

Before allocating a PTY or creating a child, the Agent opens the configured shell with the existing
no-symlink, regular-ELF, ownership, mode, and account-execution checks. It computes SHA-256 from that
already-open descriptor, rechecks inode identity, mode, owner, size, mtime, and ctime, and compares
the result to the profile. The same descriptor is later duplicated into the sealed child and used by
the final `fexecve`; path replacement cannot select different shell bytes for that launch.

For a rescue profile the parent also opens and hashes the exact Toybox path immediately before
spawn. Its trusted directory contract prevents remote or other-user replacement. The shell may
open Toybox later by path, so this is launch-time replacement detection, not an execution monitor.
Changing either payload requires an explicit new profile record and ordinary owner review.

`terminal-profile-shell-template` pins the selected shell automatically.
`terminal-profile-toolbox-template` pins both payloads automatically. The generated profile remains
disabled until reviewed and installed:

```bash
iotox --shell /opt/iotox-rescue/bin/oksh \
  --toolbox-dir /opt/iotox-rescue/bin \
  terminal-profile-toolbox-template owner-rescue > owner-rescue.profile
iotox terminal-profile-lint owner-rescue.profile
```

An absent pin is canonical `none`, which preserves local use and migration of old profiles. An
incorrect pin fails the spawn at the local policy boundary with no target process. Canonical v1--v6
records decode with both pins absent and re-encode as v7 only when explicitly rewritten.

## Nonclaims

SHA-256 is identity, not authorization or provenance. Trust comes from the owner-controlled profile
store and review of the package manifest/SBOM. A shell pin does not constrain commands the shell can
later execute, make a writable host filesystem immutable, attest the kernel, protect a stolen
unlocked machine, or supply rollback resistance for an older valid profile. A privileged process or
the trusted local file owner can still mutate an inode in place, including a narrow hash-to-exec
race; immutable/verified storage remains the deployment answer for a stronger code-integrity claim.
Those are distinct
confinement, protected-state, and witness boundaries.
ADR 0306 witnesses the Ratox host incarnation only; it deliberately does not turn that monotonic
startup record into freshness evidence for this profile or its principal binding.
