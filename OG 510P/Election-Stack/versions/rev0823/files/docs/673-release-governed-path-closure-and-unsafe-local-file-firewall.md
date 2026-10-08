# 673 — Release governed-path closure and unsafe local-file firewall

**Track:** Shared / Release engineering

This document records a v798 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

By v797, release ZIPs, manifests, builders, and extracted-tree verifiers shared a strict release path policy. However, one construction/verification seam remained: the same predicate that decides whether a path can be included in the release also returned `False` for syntactically unsafe paths.

That is correct for inclusion, but not sufficient for auditing. A governed path such as `docs/bad name.md` is not a valid release member and cannot be included in `MANIFEST.sha256`; treating it only as “not included” could let a tampered extracted tree or a dirty maintainer tree pass narrower closure checks while carrying an unsafe extra file.

Local-only paths such as `dist/`, `evidence/cache/`, interpreter caches, VCS metadata, and top-level diagnostic logs remain outside release scope. Unsafe paths outside those explicit local-only lanes must fail closed.

## Reconstruction rule

Release tooling must separate two questions:

1. **Is this path explicitly local-only?** If yes, it is ignored by release manifest/ZIP construction and extracted-tree closure.
2. **If it is not local-only, is the path release-safe?** If no, builders and verifiers must report an error instead of silently omitting it.

This keeps release path policy from becoming an accidental exclude list.

## Enforcement surfaces

v798 refactors `scripts/build_manifest.py` to expose:

- `is_local_only_rel(rel)` — explicit local-only classifier for cache/output/VCS/diagnostic debris;
- `governed_path_problem(rel)` — release-path-policy problem for any non-local-only path.

The manifest builder and deterministic ZIP builder now reject unsafe governed paths before hashing or packaging.

The extracted-tree manifest verifier now rejects unsafe governed files or directories present in the tree, even when they are not listed in `MANIFEST.sha256`. It still prunes explicit local-only directories so operator caches and local release outputs are not confused with release content.

The release-gate smoke checks now cover both sides:

- `scripts/check_release_builder_filesystem_policy.py` creates a governed filename with whitespace and requires both builders to fail closed;
- `scripts/check_manifest_verifier.py` creates an unlisted unsafe file under `docs/` and requires extracted-tree verification to fail closed.

## Operator effect

Maintainer commands are unchanged:

```bash
python3 scripts/build_manifest.py --check
python3 scripts/build_release_zip.py
python3 scripts/verify_manifest.py .
```

The difference is that unsafe governed paths now produce direct diagnostics. To keep local scratch work out of the release, place it under an explicit local-only lane such as `dist/`, `evidence/cache/`, or another already-governed cache path rather than relying on an invalid filename to evade inclusion.

## Non-claims

This is a release-scope closure guardrail. It does not add signing, timestamping, sandboxing, provenance authentication, malware scanning, or transport security. It does not change evidence-object semantics or election-process claims.

## Compression posture

This revision adds one compact maintainer-control document and extends existing stdlib checks. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or new jurisdictional claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/664-release-path-policy-safe-extraction-and-central-directory-canonicalization.md`
- `docs/667-release-manifest-tree-verifier-and-symlink-safe-hash-closure.md`
- `docs/672-release-builder-byte-exact-manifest-and-file-type-firewall.md`
- `scripts/build_manifest.py`
- `scripts/build_release_zip.py`
- `scripts/verify_manifest.py`
- `scripts/check_release_builder_filesystem_policy.py`
- `scripts/check_manifest_verifier.py`
