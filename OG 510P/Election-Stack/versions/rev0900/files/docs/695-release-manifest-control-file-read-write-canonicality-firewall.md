# 695 — Release manifest control-file read/write canonicality firewall

**Track:** Shared / Release engineering

This document records a v820 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v817 made `MANIFEST.sha256` member hashing route-aware, v818 hardened extracted-tree verifier roots, and v819 hardened manifest-builder source roots. The adjacent control-file path for `MANIFEST.sha256` itself still had a narrower gap: `scripts/build_manifest.py --check` read the checked-in manifest with ordinary `Path.read_bytes()`, and manifest regeneration wrote it with ordinary `Path.write_bytes()`.

That meant the manifest builder could correctly refuse symlinked governed members while still reading or overwriting the manifest control file itself through a local symlink or non-regular final path. Since `MANIFEST.sha256` is the archive's byte-exact release closure, its own read/write route must be at least as strict as the members it describes.

## Reconstruction rule

Manifest check/write now treats `MANIFEST.sha256` as a release control-file boundary:

- `--check` refuses a missing, symlinked, or non-regular manifest control file before parsing bytes;
- `--check` reads the control file through a no-follow route where the platform exposes directory-fd and `O_NOFOLLOW` support;
- reads recheck file identity and size after the byte stream is consumed;
- writes publish through a temporary sibling created under the no-follow parent-directory route;
- writes recheck the final `MANIFEST.sha256` target immediately before replacement;
- a final-path symlink or non-regular swap before publication fails closed instead of being followed.

The manifest remains excluded from hashing itself. This revision only hardens how the control file is read, compared, and rewritten during maintenance.

## Enforcement surfaces

v820 updates `scripts/build_manifest.py` with explicit `read_manifest_control_bytes()` and `write_manifest_control_bytes()` helpers. `check_manifest_bytes()` now uses the read helper, while the write path uses the atomic sibling helper instead of direct `Path.write_bytes()`.

v820 extends `scripts/check_release_builder_filesystem_policy.py` with manifest-control probes for symlinked control-file reads, non-regular control-file targets, and a pre-publish final-path symlink swap during manifest regeneration.

## Operator effect

Normal maintenance remains:

```text
python3 scripts/build_manifest.py
python3 scripts/build_manifest.py --check
```

The difference is fail-closed behavior if `MANIFEST.sha256` is a symlink, directory, special file, or is swapped to such a path between preflight and publication. Maintainers should keep `MANIFEST.sha256` as an ordinary checked-in file at the repository root.

## Non-claims

This does not add repository locking, does not authenticate the local filesystem namespace, and does not make arbitrary working-tree races impossible. It closes the narrower control-file seam: manifest maintenance must not follow a symlink or non-regular final path for the manifest file that defines archive hash closure.

This does not change manifest grammar, ZIP member grammar, schema semantics, voter-facing surfaces, evidence packet semantics, or election-process claims.

## Compression posture

This revision adds one compact release-engineering document and small smoke probes. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/694-release-manifest-builder-source-root-canonicality-firewall.md`
- `docs/693-release-manifest-verifier-root-lexical-canonicality-firewall.md`
- `docs/692-release-manifest-member-read-canonicality-firewall.md`
- `docs/669-release-control-file-byte-canonicality-and-crlf-firewall.md`
- `scripts/build_manifest.py`
- `scripts/check_release_builder_filesystem_policy.py`
- `scripts/verify_manifest.py`
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)
