# 680 — Release extracted-tree verification-root anchoring firewall

**Track:** Shared / Release engineering

This document records a v805 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v804 made the extracted release tree root mode canonical `0755`. The verifier checked the root after resolving it, which made the mode check correct for the target directory but still tolerated a symlinked verification root.

That meant a recipient could run:

```bash
python3 scripts/verify_manifest.py ./release-link
```

and get a pass when `./release-link` was a symlink to another directory whose bytes, modes, and `MANIFEST.sha256` were valid. The target tree was valid, but the operator-visible verification root was not a concrete extracted tree boundary. This was inconsistent with the verifier-backed safe extractor, which rejects symlink output roots and symlink-routed output ancestry before publishing.

## Reconstruction rule

An extracted Election Stack release tree is canonical only when the verifier root is a concrete directory path, not a symlink-routed alias for some other directory.

The extracted-tree verifier must therefore fail closed when the operator-supplied root path or any existing lexical root component is a symlink. It must not call `Path.resolve()` first and then verify the resolved target as though that target were the tree the operator named.

This rule keeps three boundaries aligned:

1. the archive-level verifier, which proves canonical ZIP bytes;
2. the safe extractor, which publishes a concrete output tree; and
3. the extracted-tree verifier, which proves that a named local tree has canonical release shape.

## Enforcement surfaces

v805 extends `scripts/verify_manifest.py` with a verification-root ancestry check before resolving or walking the tree. If the supplied root path traverses a symlink component, verification fails with a root-anchoring diagnostic.

The release-gate smoke coverage in `scripts/check_manifest_verifier.py` now includes a symlink-root negative probe. A minimal good tree is copied, a symlink is pointed at it, and the verifier must reject the symlink path even though the target tree itself is otherwise valid.

## Operator effect

The preferred recipient workflow remains:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN.zip
python3 scripts/extract_release_zip.py The-Election-Stack-revNNNN.zip ./election-stack-vNNNN
python3 scripts/verify_manifest.py ./election-stack-vNNNN
```

If `scripts/verify_manifest.py` reports a symlinked verification root, verify the concrete extracted directory directly or re-extract with `scripts/extract_release_zip.py`. Do not treat a symlink alias as the release tree boundary.

## Non-claims

This does not make local filesystems race-free, prevent a privileged local process from changing files after verification, or authenticate the release by itself. It only prevents the extracted-tree verifier from silently following a symlinked root and reporting that the alias path is canonical.

## Compression posture

This revision adds one compact release-engineering document and one negative probe. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/667-release-manifest-tree-verifier-and-symlink-safe-hash-closure.md`
- `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`
- `docs/674-release-safe-extractor-output-ancestry-firewall.md`
- `docs/679-release-extraction-root-mode-canonicality-firewall.md`
- `scripts/verify_manifest.py`
- `scripts/check_manifest_verifier.py`
- `scripts/extract_release_zip.py`
