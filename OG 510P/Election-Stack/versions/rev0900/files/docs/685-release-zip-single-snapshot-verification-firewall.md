# 685 — Release ZIP single-snapshot verification firewall

**Track:** Shared / Release engineering

This document records a v810 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v809 closed a carrier-name alias seam by rejecting symlink final input paths and symlink-routed input ancestry before `scripts/verify_release_zip.py` reads a release ZIP. That made the operator-supplied basename the filename whose `revNNNN`/`vNNN` tokens are checked.

One adjacent byte-boundary seam remained: after input-path preflight, the verifier still obtained release bytes through multiple path reads. It hashed the file from the filesystem path, opened the ZIP from the filesystem path, and re-read raw layout bytes from the filesystem path. A mutable local input could therefore make the verifier's hash, ZIP parser, layout parser, or canonical-rebuild comparison describe different moments of the same path.

The normal release lane uses immutable artifacts, so this is not a new election-process claim. It is a verifier reconstruction issue: the artifact verdict should be about one byte string, not about a path that may be re-read at several stages.

## Reconstruction rule

The release ZIP verifier now treats archive verification as a single-snapshot operation:

- reject symlink final paths and symlink-routed ancestry before the snapshot, preserving the v809 carrier-name rule;
- open the candidate ZIP through a regular-file handle, using `O_NOFOLLOW` where the platform exposes it;
- read the candidate bytes exactly once into an immutable in-memory snapshot;
- compute the reported ZIP SHA-256 from that snapshot;
- parse ZIP members, raw EOCD/local/central-directory layout, in-ZIP manifest hashes, and the canonical rebuild comparison from that same snapshot;
- fail closed if the opened file's size changes while the snapshot is being read.

This means a verifier report cannot accidentally combine the hash of one byte stream with the central directory or manifest of another byte stream.

## Enforcement surfaces

v810 tightens `scripts/verify_release_zip.py` by introducing a single `_read_zip_snapshot()` boundary and by changing ZIP parsing/layout checks to operate on `io.BytesIO(snapshot)` plus the same raw `bytes` buffer.

v810 also extends `scripts/check_release_zip_verifier.py` with a regression probe that snapshots a valid archive and then mutates the filesystem path before the rest of verification runs. The verifier must still succeed against the snapshotted bytes and must report the hash of those snapshotted bytes. If a later refactor reintroduces path re-reads after the snapshot boundary, that probe fails.

Existing negative probes remain in place for filename-token disagreement, padded semantic filename tokens, symlink input aliases, hash mismatches, CRLF control files, duplicate members, unsafe paths, whitespace/reserved/case/shape collisions, non-canonical modes, overlays, preambles, and non-stored compression.

## Operator effect

Operator usage is unchanged:

```text
python3 scripts/verify_release_zip.py dist/The-Election-Stack-rev0810.zip
```

The emitted `sha256=` value is now explicitly the hash of the verifier's single byte snapshot. Operators should still verify immutable files from a concrete local path and should still avoid symlink aliases as described in `docs/684-release-zip-input-symlink-alias-firewall.md`.

## Non-claims

This does not make a mutable local filesystem an acceptable release medium, does not introduce file locking, and does not attempt to prove that an artifact path remains unchanged after verification finishes. It only makes each verifier invocation internally coherent by binding all archive checks to one opened byte snapshot.

This does not change release ZIP member names, manifest grammar, schema semantics, voter-facing surfaces, evidence packet semantics, or election-process claims.

## Compression posture

This revision adds one compact release-engineering document and one verifier regression probe. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/684-release-zip-input-symlink-alias-firewall.md`
- `docs/683-release-filename-version-token-coherence-firewall.md`
- `scripts/verify_release_zip.py`
- `scripts/check_release_zip_verifier.py`
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)
