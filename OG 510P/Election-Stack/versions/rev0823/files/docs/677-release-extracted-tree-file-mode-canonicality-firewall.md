# 677 — Release extracted-tree file-mode canonicality firewall

**Track:** Shared / Release engineering

This document records a v802 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

By v801, the release ZIP itself had strict member-mode canonicality: `scripts/verify_release_zip.py` required every archive member to carry canonical `0644` mode metadata, and `scripts/extract_release_zip.py` wrote extracted release files with `0644` permissions.

The extracted-tree verifier still focused on bytes, path names, regular-file status, and manifest closure. That meant a recipient could unpack with a different tool, accidentally preserve or add executable bits, and still get a passing `scripts/verify_manifest.py` verdict as long as file bytes matched `MANIFEST.sha256`.

File mode drift is not a content hash failure, but it is release-shape drift. The published tree should not grow executable or locally permissive semantics outside the canonical archive contract.

## Reconstruction rule

An extracted Election Stack release tree is canonical only when every release-scope payload file is an ordinary file with mode `0644`:

1. `MANIFEST.sha256` continues to seal payload bytes, not local filesystem metadata.
2. `scripts/verify_release_zip.py` continues to reject non-`0644` ZIP member metadata.
3. `scripts/extract_release_zip.py` continues to write extracted files as `0644`.
4. `scripts/verify_manifest.py` now rejects release-scope files whose extracted mode is not `0644`.
5. Local-only cache/output lanes remain outside release scope, but governed release paths must not silently carry executable-bit drift.

This makes the recipient-side tree verifier agree with the archive verifier and the official safe extractor on the file-mode part of the release shape.

## Enforcement surfaces

v802 changes `scripts/verify_manifest.py` to inspect every release-scope regular file with `stat(follow_symlinks=False)` after symlink and regular-file checks. Any mode other than `0644` is a verification problem.

v802 also extends `scripts/check_manifest_verifier.py` with a negative probe that changes a manifested file to `0755` while keeping its bytes and manifest digest unchanged. The extracted-tree verifier must reject that tree by mode canonicality, proving the check is not merely a byte-hash check.

## Operator effect

The preferred recipient workflow is unchanged:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN.zip
python3 scripts/extract_release_zip.py The-Election-Stack-revNNNN.zip ./election-stack-vNNNN
python3 scripts/verify_manifest.py ./election-stack-vNNNN
```

If a tree verifies as a ZIP but fails after extraction by file mode, re-extract with `scripts/extract_release_zip.py` or normalize the tree through a controlled, auditable reconstruction step. Do not treat executable-bit drift as harmless when publishing or redistributing the extracted release tree.

## Non-claims

This does not make POSIX permissions a security boundary, does not sandbox hostile filesystems, and does not sign the archive. It only aligns the extracted-tree verifier with the canonical mode already enforced by the release ZIP verifier and the official extractor.

## Compression posture

This revision adds one compact release-engineering document and extends an existing manifest-verifier smoke test. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/663-release-zip-permission-canonicalization-and-extraction-rebuild-invariance.md`
- `docs/667-release-manifest-tree-verifier-and-symlink-safe-hash-closure.md`
- `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`
- `scripts/verify_release_zip.py`
- `scripts/extract_release_zip.py`
- `scripts/verify_manifest.py`
- `scripts/check_manifest_verifier.py`
