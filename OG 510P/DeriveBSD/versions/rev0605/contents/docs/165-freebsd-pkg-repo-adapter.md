# FreeBSD pkg repository adapter (optional): bridge Derive artifacts to pkg tooling

DeriveBSD’s native distribution model is: digest-identified objects + signatures + attestations.
FreeBSD has an established ecosystem for distributing binary packages via **pkg** repositories.

This document defines an **optional adapter lane**:
- export a subset of Derive artifacts as a **pkg repo**
- verify (and, if desired, produce) pkg repo signatures in a policy-governed way

The goal is compatibility and incremental adoption, not turning DeriveBSD into “pkg with extra steps”.

## Why this is useful

- Many FreeBSD operators already rely on `pkg` workflows.
- Enterprises often have internal `pkg` mirrors.
- A pkg-shaped output can be a pragmatic on-ramp while Derive-native tooling matures.

## Adapter design

### Export

- Take a Derive artifact set (closure-selected) and map it to:
  - pkg packages (when available)
  - or “bundle packages” that contain prebuilt payloads (narrow, v0)

Export MUST preserve Derive identity:
- every exported package includes the Derive artifact digest in metadata
- the repo includes a `derive.repo.manifest` that maps pkg names → Derive digests

### Signing and verification

FreeBSD pkg supports repository signature verification with multiple signature modes.
DeriveBSD should:
- treat repo signing as a **crypto operation** (split-crypto domain compatible)
- record signature configuration in policy decision records

### Consumption

If a DeriveBSD node consumes packages from a pkg repo:
- it MUST still verify the underlying Derive digests and required attestations
- pkg signatures can be treated as an *additional* compatibility check, not the source of truth

## Non-goals

- Replacing Derive caches with pkg repos.
- Accepting “pkg says it’s fine” as sufficient verification.

## References

- pkg.conf(5) repository signature modes (`SIGNATURE_TYPE`): https://man.freebsd.org/cgi/man.cgi?query=pkg.conf
- pkg-repo(8) repository metadata and signatures: https://man.freebsd.org/pkg-repo%288%29

See also: `docs/108-ports-pkg-adapter-lane.md`, `docs/46-cache-trust-model.md`.

Last updated: 2026-02-23
