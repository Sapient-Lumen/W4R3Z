# ADR 0094: commit immutable synchronization objects before the signed HEAD

- Status: accepted and implemented locally
- Date: 2026-08-20
- Scope: local synchronization publication ordering and immutable object boundary
- Depends on: ADR 0093 and signed synchronization HEAD v1

## Context

The signed HEAD names both an artifact and a manifest, but a signature alone cannot prove either
object exists or contains the named bytes. Publishing the HEAD before durable object verification
would expose a valid but unavailable revision. Hashing only the source before copying also leaves a
time-of-check/time-of-use window in which a changing source can be committed under the old identity.

## Decision

1. Local publication accepts two absolute regular-file sources: artifact and manifest.
2. Both nonempty inputs must fit their independent namespace bounds and their combined bytes must fit
   the per-publication store bound before any namespace directory is created.
3. Each source is hashed through the injected cryptographic seam, copied through a bounded private
   randomly named staging file, published with no-clobber linkage, and then re-sized and re-hashed at
   its final object path. Stale staging debris cannot reserve a future process/PID filename.
4. Existing objects are reusable only when they are owner-owned, mode 0600, single-link regular files
   whose exact size and digest match their filename identity.
5. Namespace, object, and staging paths must be real owner-owned directories; source symlinks are
   refused.
6. The stable-device signed HEAD advances only after both final objects verify and a last cancellation
   check passes. Failure or cancellation never changes the HEAD. Already committed unreferenced
   immutable objects may remain and are safe to reuse or later collect.
7. The same post-copy verification now protects the earlier accepted-artifact installation path.

## Consequences

- A successful local publication result proves that both objects existed durably and matched the
  identities signed into its HEAD at commit time.
- Exact retries reuse verified objects and return the existing HEAD without consuming a generation.
- Source mutation during copy fails closed and removes the newly mismatched object before any HEAD
  commit.
- This is still a local transport-neutral job. It does not grant authority, accept remote input,
  enforce whole-store retention across all revisions, or activate content.

## Rejected alternatives

### Publish the HEAD and fetch missing objects later

Rejected for the local writer because it deliberately creates signed unavailable revisions and makes
an interrupted publication indistinguishable from a remote availability failure.

### Trust the source hash after copying

Rejected because the source path can change between hashing and copying. The final object itself is
the commitment boundary and must be verified there.

### Embed manifest bytes in the HEAD

Rejected because the fixed HEAD must remain a small bounded control record while manifests and
artifacts use the immutable bulk path.
