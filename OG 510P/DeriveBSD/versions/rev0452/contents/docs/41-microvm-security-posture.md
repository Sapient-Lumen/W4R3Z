# MicroVM security posture (v1)

This doc prevents “security regression by convenience.”

## Defaults (v1)
- Virtio baseline only (virtio-net/blk/console).
- No PCI passthrough by default (ADR-0006).
- No host filesystem mounts into guests (except explicit RO metadata disks).
- Prefer running bhyve workers inside a jail when supported (defense in depth).
- Deny inbound networking by default; explicit egress policy.
- Secrets never baked into images; injected via explicit channel + policy.
- Audit every run decision (digests + actor + policy result).

## Escape hatches
Higher-risk features (passthrough, privileged networking) require:
- explicit policy allow
- higher assurance host profile
- additional auditing

Additional escape hatches:
- virtio-9p host↔guest filesystem sharing (optional) must be read-only and non-secret (see `docs/124-virtio-9p-injection-channel.md`).
- running bhyve outside a jail must be an explicit policy choice when jailed workers are available (see `docs/121-jailed-hypervisor-workers.md`).

See ADR-0006 and `docs/54-host-hardening-profile.md`.
Last updated: 2026-02-23
