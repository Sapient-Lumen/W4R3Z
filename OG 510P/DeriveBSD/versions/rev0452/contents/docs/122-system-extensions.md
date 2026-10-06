# System extensions (immutable base + optional debug layers)

Immutable, rollbackable bases create a predictable operational pain:
**debug/forensics tools** (strace/gdb/etc.) are invaluable during incidents, but bundling them into the base grows the TCB and attack surface.

systemd’s “system extension images” are a clean pattern to steal: attach a read-only image that *extends* `/usr` (and/or `/opt`) **without modifying** the underlying base image.

Reference:
- systemd-sysext(8): https://www.freedesktop.org/software/systemd/man/systemd-sysext.html

## DeriveBSD mapping (ZFS-native)

DeriveBSD can implement a similar concept with ZFS datasets and mount ordering:

- Base generation: `zfs://.../GEN/<digest>` (read-only)
- Extension bundles: `zfs://.../EXT/<digest>` (read-only)
- Activation composes a *view*:
  - mount base
  - mount extensions over a narrow prefix (e.g. `/usr/local/derive-ext/<name>`)
  - optionally union into `/usr` via a controlled mechanism (policy-gated)

**Key property:** the running system is still explainable as:
`base_digest + [ext_digest...] + activation_policy`.

## Limits (borrowed from systemd-sysext lessons)

System extension images activate **after** the relevant filesystems are mounted, so they are not suitable for resources required in the *earliest boot* phase.
In particular, avoid shipping foundational system services or earliest-boot configuration through extensions.

Reference:
- systemd-sysext(8) notes on suitability/boot timing: https://man.archlinux.org/man/systemd-sysext.8.en

## Policy + safety invariants

- Extensions are **signed artifacts** with their own provenance.
- Extensions are **not** allowed to change boot-critical bytes unless the policy explicitly permits it.
- Extensions can be “incident-only” (timeboxed validity) to avoid permanent drift.

## What this buys

- Debuggability without growing the immutable base
- Small “ops tools” bundles for incident response
- Cleaner separation between *platform* and *operator tooling*

## Evidence objects

Record in the activation report:
- base generation digest
- extension digests
- mount map
- policy decision id

Last updated: 2026-02-23
