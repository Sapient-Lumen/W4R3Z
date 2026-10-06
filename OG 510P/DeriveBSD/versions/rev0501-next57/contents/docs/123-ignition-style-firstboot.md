# Ignition-style first boot provisioning (pattern)

Many “immutable OS” systems still need to *mutate disks* exactly once: create users, lay down config files, partition/format disks, etc.
Fedora CoreOS uses **Ignition** for this: it runs in initramfs and provisions disk state from a declarative JSON config, then the system boots normally.

References:
- Fedora CoreOS docs (producing an Ignition config): https://docs.fedoraproject.org/en-US/fedora-coreos/producing-ign/
- Ignition overview: https://coreos.github.io/ignition/
- Ignition configuration spec (example v3.4.0): https://coreos.github.io/ignition/configuration-v3_4/

## Why this pattern is attractive for DeriveBSD

- Disk mutations are **explicit** and happen at a well-defined phase.
- The config is an *input artifact* that can be hashed, signed, reviewed.
- After first boot, the steady-state runtime remains immutable/rollbackable.

## DeriveBSD mapping

DeriveBSD already has “explicit config + secrets injection.”
Ignition suggests splitting it into:

1) **First-boot provisioning** (one-shot):
   - create datasets
   - write static config files
   - initialize identity material containers (not secrets)
2) **Per-boot injection** (recurring):
   - rotate secrets
   - per-instance config
   - runtime policy decisions

In other words: *provision once, inject always.*

## Evidence + explainability

Treat the first-boot config as a signed input and record:
- config digest
- policy decision id
- resulting disk layout digest(s) (ZFS dataset tree hash or equivalent)

## Practical implementation notes

- For microVM images, a minimal “provisioner init” can run before the workload (similar to Ignition’s initramfs role).
- For host systems, provisioning can happen during activation of a new boot environment, but must remain atomic/rollbackable.

Last updated: 2026-02-23
