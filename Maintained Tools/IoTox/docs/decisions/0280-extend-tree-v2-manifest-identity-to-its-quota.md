# ADR 0280: Extend tree-v2 manifest identity to its quota

Status: accepted, 2026-09-01

## Context

The adversarial maximum-tree test found a contract mismatch. Namespace policy admits a 4 MiB,
4,096-entry manifest, but IoTox's general one-shot domain-separated hash API intentionally refuses
inputs above 64 KiB. Small tree-v2 manifests worked; a valid large manifest could be encoded but
could not receive the digest needed by a branch HEAD.

Lowering the advertised manifest/object quotas would hide the mismatch and discard useful bounded
capacity. Removing the general hash bound would widen an application-wide allocation contract.

## Decision

Preserve the existing `iotox-sync-tree-v2-manifest-v1` digest byte for every manifest that was
previously hashable. If and only if that exact one-shot operation refuses the size, split the
canonical encoded manifest into ordered 60 KiB chunks. Each leaf commits its index, chunk count,
complete byte count, and bytes under `iotox-sync-tree-v2-manifest-chunk-v1`. A small `IOTXTMH1` root
commits the ordered leaf vector, count, and complete byte count under
`iotox-sync-tree-v2-manifest-chunk-root-v1`.

The maximum namespace manifest yields fewer than 70 bounded leaves and a root far below the existing
hash ceiling. No peer frame, manifest encoding, branch encoding, or former object identity changes.
Former peers could not author or accept one of these larger HEADs because their local digest step
already failed.

## Consequences

The default 4,096-entry tree ceiling is now real rather than nominal. Tests exercise scan, unique CAS
import, signed branch creation, merge, and complete projection at that ceiling. The general Sodium
hash input bound remains unchanged, and manifests beyond the namespace byte/object quotas still fail
before hashing.
