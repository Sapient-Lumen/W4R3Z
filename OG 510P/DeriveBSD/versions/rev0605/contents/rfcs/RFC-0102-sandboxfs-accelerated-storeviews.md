# RFC-0102: sandboxfs-accelerated store views (optional)

Status: Draft

## Summary

Introduce an optional storeview projection mechanism based on `sandboxfs` (FUSE) to reduce mount/symlink overhead for large closures, while preserving the store view minimization contract.

## Motivation

Mount-per-input is security-correct but can be costly at scale. Bazel uses sandboxfs specifically to make sandbox setup fast.
FreeBSD has a sandboxfs port, making this plausible on DeriveBSD hosts.

## Design sketch

- `storeview.manifest` remains the canonical input.
- Add `sandbox.storeview.strategy` with values:
  - `nullfs` (baseline)
  - `sandboxfs` (optimization)
- Include the chosen strategy in the Plan digest.

## Security

- sandboxfs runs outside the hostile build sandbox.
- mapping is derived deterministically from the Plan.
- store paths remain read-only; outputs remain separate.

## Alternatives

- view pooling + prefix compaction (keep existing), but still can hit scaling limits.

## References

- Bazel sandboxing / sandboxfs note: https://bazel.build/docs/sandboxing
- sandboxfs repo: https://github.com/bazelbuild/sandboxfs
- FreeBSD port: https://www.freshports.org/filesystems/sandboxfs/

