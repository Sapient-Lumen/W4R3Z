# 694 — Release manifest builder source-root canonicality firewall

**Track:** Shared / Release engineering

This document records a v819 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v817 made manifest member hashing route-aware, and v818 made extracted-tree manifest verification reject ambiguous explicit verifier roots. The adjacent construction-side source root for `MANIFEST.sha256`, however, was still anchored with `Path(__file__).resolve().parents[1]`.

That is convenient for normal execution, but `resolve()` follows symlinks before the builder has audited the route it is about to manifest. A maintainer running the manifest builder through a symlinked checkout alias could therefore produce `MANIFEST.sha256` for the target tree while the audit-visible script route named a different source-root path.

The release ZIP builder had already learned to reject ambiguous or symlink-routed source roots in v814. Manifest generation needed the same construction-side root rule so the two construction surfaces do not diverge.

## Reconstruction rule

Manifest construction now treats the manifest source root as a concrete release input boundary:

- empty source-root paths fail;
- NUL-containing source-root paths fail;
- trailing separators fail;
- repeated separator components fail;
- `.` and `..` components fail before tree walk or hashing;
- missing roots fail;
- non-directory roots fail;
- symlink final roots fail;
- symlinked source-root ancestry fails.

The module default still points to the repository that contains `scripts/build_manifest.py`, but it is now recorded as an absolute lexical path rather than a symlink-resolved path. `build_manifest_entries()` preflights that root before walking the tree or hashing any member.

## Enforcement surfaces

v819 updates `scripts/build_manifest.py` so manifest generation preflights `ROOT` with lexical path checks and symlink-ancestry checks before `rglob()` discovery. The no-follow member reader added in v817 remains in force for each selected manifest member.

v819 extends `scripts/check_release_builder_filesystem_policy.py` with manifest source-root probes for current-directory components, repeated separators, trailing separators, non-directory roots, final-root symlinks, and symlinked parent routes.

## Operator effect

Normal manifest maintenance remains:

```text
python3 scripts/build_manifest.py
python3 scripts/build_manifest.py --check
```

Maintainers should run the manifest builder from a concrete checkout path, not through a symlinked checkout alias or a path spelling that depends on `./`, `../`, repeated separators, or a trailing separator.

## Non-claims

This does not add filesystem locking, does not authenticate the local path namespace, and does not make a mutable working tree race-free. It closes a narrower construction ambiguity seam: manifest generation must not silently convert a symlink-routed script/source-root path into a different canonical target before deciding which tree is being manifested.

This does not change manifest grammar, ZIP member grammar, schema semantics, voter-facing surfaces, evidence packet semantics, or election-process claims.

## Compression posture

This revision adds one compact release-engineering document and manifest-builder source-root probes. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/693-release-manifest-verifier-root-lexical-canonicality-firewall.md`
- `docs/692-release-manifest-member-read-canonicality-firewall.md`
- `docs/689-release-zip-builder-source-root-canonicality-firewall.md`
- `docs/680-release-extracted-tree-verification-root-anchoring-firewall.md`
- `scripts/build_manifest.py`
- `scripts/check_release_builder_filesystem_policy.py`
- `scripts/verify_manifest.py`
- `scripts/build_release_zip.py`
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)
