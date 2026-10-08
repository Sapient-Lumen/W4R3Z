# 679 — Release extraction-root mode canonicality firewall

**Track:** Shared / Release engineering

This document records a v804 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v803 made extracted release directories below the tree root canonical: each governed directory had to be implied by `MANIFEST.sha256` and have mode `0755`. The official safe extractor normalized those child directories before running `scripts/verify_manifest.py`.

The remaining metadata seam was the extraction root itself. Because the safe extractor publishes a temporary directory created by `tempfile.mkdtemp()`, the final output directory could be `0700` even though every release child directory was `0755` and every manifested file byte matched. That meant two safely extracted copies could have the same archive hash, manifest hash, file hashes, and child-directory shape while disagreeing on the published root mode.

The root is operator-selected and is not a ZIP member, but it is still part of the recipient-visible release tree. A verifier-backed extractor should publish a canonical tree boundary, not leave that boundary to local temporary-directory defaults.

## Reconstruction rule

An extracted Election Stack release tree is canonical only when:

1. the extraction root directory itself has mode `0755`;
2. every release-scope directory below the root has mode `0755` and is implied by a manifest path;
3. every release-scope regular file has mode `0644` and is listed in `MANIFEST.sha256`;
4. explicit local-only lanes remain outside release scope; and
5. unsafe governed paths, symlinks, and non-regular nodes fail closed.

This closes the one-mode gap between the published tree boundary and the release directories below it.

## Enforcement surfaces

v804 extends `scripts/verify_manifest.py` so the extracted-tree verifier inspects the root directory mode before checking manifest closure. A tree whose root is `0700`, `0777`, or otherwise non-canonical now fails even when all file bytes match.

v804 also updates `scripts/extract_release_zip.py` so the official safe extractor normalizes the temporary extraction root to `0755` before post-extraction verification and final rename. The final published directory therefore has the same mode expected by `scripts/verify_manifest.py`.

The release-gate smoke coverage is extended in two places:

- `scripts/check_manifest_verifier.py` includes a root-mode drift negative probe.
- `scripts/check_release_safe_extractor.py` confirms the safe extractor publishes a `0755` output root as well as `0755` child directories.

## Operator effect

The preferred recipient workflow remains:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN.zip
python3 scripts/extract_release_zip.py The-Election-Stack-revNNNN.zip ./election-stack-vNNNN
python3 scripts/verify_manifest.py ./election-stack-vNNNN
```

If a manually unpacked tree fails only because the root directory mode drifted, normalize the root to `0755` or re-extract with `scripts/extract_release_zip.py`. Do not reseal or redistribute a tree whose boundary metadata has not been verified.

## Non-claims

This does not make POSIX directory modes a sandbox, authenticate the release, or protect against a hostile filesystem. It only makes the extracted-tree verifier and safe extractor agree on the canonical recipient-visible tree boundary.

## Compression posture

This revision adds one compact release-engineering document and extends existing verifier/extractor smoke checks. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/667-release-manifest-tree-verifier-and-symlink-safe-hash-closure.md`
- `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`
- `docs/677-release-extracted-tree-file-mode-canonicality-firewall.md`
- `docs/678-release-extracted-tree-directory-closure-and-mode-canonicality-firewall.md`
- `scripts/extract_release_zip.py`
- `scripts/verify_manifest.py`
- `scripts/check_manifest_verifier.py`
- `scripts/check_release_safe_extractor.py`
