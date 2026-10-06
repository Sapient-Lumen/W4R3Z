# RFC-0081: Syspatch-like signed patchsets

Status: Draft

## Summary

Introduce a **patchset artifact** lane for urgent binary updates to base sets or host generations.
Patchsets are signed, revertible, and policy-bounded.

Reference model: OpenBSD `syspatch` (fetch/verify/install/revert; rollback tarball generation). https://man.openbsd.org/syspatch.8

## Goals

- Fast application of small critical fixes.
- Preserve explainability (why/what/where-from) via policy decision records.
- Rollback is always available.

## Design sketch

- New artifact kind: `patchset`.
- Patchset binds to:
  - target base-set digest OR target host-generation digest
  - replacement file digests
  - rollback payload digest
  - expiry / revocation metadata

See: `docs/113-syspatch-style-patchsets.md` and `docs/102-emergency-grafts.md`.
