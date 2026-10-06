# Derived recovery images and minimal userspace (LinuxBoot/u-root lessons)

Immutable systems fail in two ways:

1) they’re hard to mutate accidentally (good)
2) they’re hard to repair intentionally (bad)

DeriveBSD already treats installer and recovery workflows as derived operations.
This doc tightens the *repair ergonomics* by stealing a LinuxBoot/u-root idea:

> build a tiny, composable recovery userspace as a normal artifact, not a one-off ISO.

## Goals

- Recovery environments are **reproducible artifacts** derived from the same inputs as the host.
- “Breakglass” and “installer” tooling share a minimal base (less drift).
- Recovery actions emit the same **evidence receipts** as normal operations.

## The pattern

LinuxBoot/u-root demonstrates a useful shape:

- minimal kernel + initramfs
- a small set of statically-linked tools
- fast iteration (the recovery environment is “just another build output”)

DeriveBSD analog:

- a **recovery capsule** built from the Derive pipeline
- can be embedded into a Unified Boot Capsule (`docs/358-…`) or shipped as a separate artifact
- tools are capability-mediated (no ambient mount/network unless policy grants it)

Product-shape note: recovery-image presence and authority are now profile-shaped defaults in `docs/473-installation-and-recovery-posture-by-profile.md`; this doc stays focused on the derived-userspace shape.

## Safety requirements

A recovery environment is high privilege. Make it safer by default:

- it boots into a **restricted mode** (read-only by default)
- mutation requires explicit grants (breakglass leases, consent workflows)
- it records all operations as receipts (disk layout applies, ZFS sends, key operations)

## Where this plugs in

- Installer + recovery as derived operations: `docs/309-installation-and-recovery-as-derived-operations.md`
- Breakglass + recovery workflows: `docs/250-breakglass-and-recovery-workflows.md`
- Breakglass grants + receipts: `spec/breakglass.grant.schema.json`, `spec/breakglass.receipt.schema.json`

## References

- LinuxBoot overview:
  https://book.linuxboot.org/
- u-root releases (one-binary initramfs userspace):
  https://github.com/u-root/u-root/releases
- LWN: replacing x86 firmware with Linux and Go (LinuxBoot context):
  https://lwn.net/Articles/738649/

Last updated: 2026-03-06r202