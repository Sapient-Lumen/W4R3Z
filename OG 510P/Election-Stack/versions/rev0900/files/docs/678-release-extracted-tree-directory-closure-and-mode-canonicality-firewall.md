# 678 — Release extracted-tree directory closure and mode canonicality firewall

**Track:** Shared / Release engineering

This document records a v803 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

By v802, extracted-tree verification rejected byte-preserving file-mode drift: a manifested file with correct SHA-256 bytes but non-canonical `0755` mode could no longer pass `scripts/verify_manifest.py`.

The remaining extracted-tree shape seam was directory metadata and empty governed directories. `MANIFEST.sha256` seals files, not directories, and the official ZIP does not carry directory entries. A recipient tree could therefore contain an extra governed empty directory, or a required release directory with locally drifted mode, while every manifested file byte still matched.

That is not a payload-hash failure, but it is release-tree shape drift. The canonical extracted tree should contain exactly the governed directories implied by manifest paths, and those directories should have a deterministic mode.

## Reconstruction rule

An extracted Election Stack release tree is canonical only when:

1. every release-scope regular file is listed in `MANIFEST.sha256` and has mode `0644`;
2. every release-scope directory below the tree root is an ancestor of at least one manifest path;
3. every release-scope directory below the tree root has mode `0755`;
4. explicit local-only lanes such as `dist/`, interpreter caches, VCS metadata, and top-level diagnostic logs remain outside release scope;
5. unsafe governed directories still fail closed rather than becoming silent exclusions.

The tree root itself is not treated as a release member because it is the operator-selected publication directory. The canonicality rule applies to release directories below that root.

## Enforcement surfaces

v803 extends `scripts/verify_manifest.py` so it collects release-scope directories while walking the extracted tree. The verifier now rejects:

- release-scope directories whose mode is not `0755`;
- release-scope directories that are not implied by any manifest entry path;
- symlinked or unsafe governed directories before descent.

v803 also updates `scripts/extract_release_zip.py` so the official safe extractor normalizes release directories below the temporary extraction root to `0755` before the post-extraction manifest verifier runs.

The release-gate smoke coverage in `scripts/check_manifest_verifier.py` now includes both a directory-mode drift probe and a stray empty-directory probe. `scripts/check_release_safe_extractor.py` also confirms the official extractor publishes canonical release-directory modes.

## Operator effect

The preferred recipient workflow is unchanged:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN.zip
python3 scripts/extract_release_zip.py The-Election-Stack-revNNNN.zip ./election-stack-vNNNN
python3 scripts/verify_manifest.py ./election-stack-vNNNN
```

If a manually unpacked tree fails because a release directory is extra or mode-drifted, re-extract with `scripts/extract_release_zip.py` or remove the local directory and normalize permissions through an auditable reconstruction step before redistribution.

## Non-claims

This does not make POSIX directory modes a security boundary, sandbox hostile filesystems, or sign the archive. It only aligns recipient-side extracted-tree verification with the canonical regular-file tree shape already implied by the manifest and official safe extractor.

## Compression posture

This revision adds one compact release-engineering document and extends existing verifier/extractor smoke checks. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/667-release-manifest-tree-verifier-and-symlink-safe-hash-closure.md`
- `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`
- `docs/677-release-extracted-tree-file-mode-canonicality-firewall.md`
- `scripts/extract_release_zip.py`
- `scripts/verify_manifest.py`
- `scripts/check_manifest_verifier.py`
- `scripts/check_release_safe_extractor.py`
