# MicroVM artifact target (bundle + manifest + injection)

MicroVMs should be **first-class artifacts** produced by Derive, not a separate workflow.

See:
- `docs/33-runtime-manifest-schema.md`
- `docs/34-microvm-bundle-format.md`

---

## Artifact definition

A microVM artifact is a bundle containing:
- **root filesystem** (disk image or filesystem tree)
- optional **kernel** + boot config (depends on guest model)
- **runtime manifest** (resources/devices/networks)
- **config injection bundle** (non-secret)
- **signature + provenance metadata** (always)

Invariant: the artifact is immutable and verifiable.

---

## Image formats (pick one for v1)

Options:
- Raw disk image (simple)
- qcow2 (features, complexity)
- ZFS zvol-backed (fast clones on ZFS hosts)

Recommendation:
- Prefer **ZFS-native** on FreeBSD/ZFS (zvol + snapshots/clones)
- Provide a raw fallback format for tooling compatibility

---

## Config and secrets injection

Standardized separately to avoid duplication:
- See `docs/28-config-and-secrets-injection.md` (RFC-0012).

## Rollback semantics

Rollback is “switch image pointer and restart microVM”.
On ZFS hosts, overlays can be rolled back via snapshot revert + pointer switch.

---

## Required introspection

- `derive explain <microvm>` shows:
  - image hash + signing key
  - manifest digest
  - closure size
  - config/secrets interfaces

## Target framework pointer

See `docs/73-artifact-target-framework.md` (RFC-0047, ADR-0020) for the unified target abstraction.


Last updated: 2026-02-23
