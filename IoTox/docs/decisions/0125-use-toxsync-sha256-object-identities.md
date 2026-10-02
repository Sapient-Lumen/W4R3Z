# ADR 0125: use toxsync SHA-256 immutable-object identities

Status: accepted, 2026-08-21.

## Decision

IoTox synchronization artifact and manifest identities are SHA-256 digests. The implementation reuses
the preserved toxsync portable `Sha256` primitive through an IoTox-owned file-hash entrance. Signed
HEAD records, authority records, rollback guards, and other IoTox metadata retain their existing
domain-separated BLAKE2b-256 contracts.

The production file entrance opens an absolute path with `O_NOFOLLOW`, requires a regular file, hashes
the descriptor in bounded chunks, and compares device, inode, mode, link count, owner, size, mtime,
ctime, and observed byte count before accepting the digest. A path replacement, mutation, truncation,
growth, symlink, directory, or read error fails closed.

## Why

The preserved toxsync content store, manifests, range planner, and published identities already use
SHA-256. Choosing another object digest in the Agent adapter would require translating every identity
or maintaining parallel object stores, defeating reuse and making wire records ambiguous. Metadata
signing domains and content identities solve different problems and need not use the same primitive.

## Consequences

- The object scheduler and attempt journal's 32-byte `Digest` field means SHA-256 for artifact and
  manifest content.
- The complete signed-HEAD record digest remains the existing IoTox domain-separated BLAKE2b-256
  value; object requests therefore bind both contracts without aliasing them.
- Empty files have a valid SHA-256 value, although the current namespace policy deliberately rejects
  zero-byte artifacts and manifests.
- This decision does not claim resistance to a privileged local writer mutating store files. Strict
  shape checks and remote digest verification turn such mutation into detected failure, not authority.
