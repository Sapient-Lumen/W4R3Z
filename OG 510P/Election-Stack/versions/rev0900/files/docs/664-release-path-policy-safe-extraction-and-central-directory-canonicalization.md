# 664 — Release path policy, safe extraction, and central-directory canonicalization

**Track:** Shared / Release engineering

This document records a v790 packaging hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

The v789 release made release ZIPs rebuild byte-for-byte after stdlib extraction and made ZIP member modes canonical. The next audit seam was path handling around those release surfaces.

Three risks were small but worth closing:

1. manifest and ZIP predicates normalized paths locally, so future changes could reintroduce trimming or character-set stripping that hides leading dots or whitespace-bearing names before exclusions see them;
2. extraction probes used ordinary ZIP extraction after a string-prefix containment check, which is less precise than checking a resolved destination with `Path.relative_to` and then writing the member explicitly;
3. the ZIP verifier checked local-record layout and `zipfile` metadata, but did not parse every central-directory field as raw bytes, leaving creator-system, version-needed, central flags, DOS timestamp words, internal attributes, and local-header offsets less explicitly sealed.

None of these were observed as shipped payload failures in v789. They are release-engineering firewalls against future drift.

## Reconstruction rule

`scripts/release_path_policy.py` is now the shared stdlib-only path policy for release members. A release path must be a POSIX-style repository-relative ASCII name and must not contain:

- an empty, current-directory, or parent-directory path component;
- a leading slash, drive-like leading component, or backslash;
- a trailing slash / directory entry shape;
- leading or trailing whitespace;
- whitespace inside any component;
- ASCII control characters or non-ASCII characters.

A literal leading `./` remains presentation noise and may be removed. Nothing else is trimmed. In particular, leading-dot paths such as `.git/config` stay visible to the explicit VCS exclusion rule rather than being rewritten into a different path.

`scripts/build_manifest.py`, `scripts/build_release_zip.py`, and `scripts/verify_release_zip.py` now use this policy. The deterministic ZIP builder also pins ZIP creator/extractor metadata (`create_system=Unix`, ZIP 2.0) so the central directory does not depend on the maintainer's platform.

## Safe extraction rule

`scripts/check_release_zip_rebuild_from_extract.py` no longer delegates extraction to `ZipFile.extractall()` after a string-prefix containment test. It now resolves each member destination through `scripts/release_path_policy.py::safe_extract_destination()` and writes the file only if the destination is inside the extraction root according to `Path.relative_to` semantics.

This matters because `/tmp/outside` starts with the characters `/tmp/out` but is not inside `/tmp/out`. Release extraction checks must use path relationships, not string prefixes.

## Central-directory rule

`scripts/verify_release_zip.py` now parses central-directory records directly and requires canonical agreement with the local headers and `zipfile` view:

- central names match the member names;
- version-made-by and version-needed are canonical;
- general-purpose flags are zero;
- compression method is `ZIP_STORED`;
- DOS timestamp words match the fixed release timestamp;
- CRC, compressed size, uncompressed size, external attributes, and local-header offsets agree;
- central extra fields, per-file comments, nonzero disk starts, and internal attributes are rejected.

The existing local-header, EOCD, overlay, preamble, manifest-closure, and per-entry SHA-256 checks remain in force.

## Release-gate placement

The early packaging lane is now:

1. `scripts/check_no_cache_artifacts.py`;
2. `scripts/check_no_symlinks.py`;
3. `scripts/check_release_path_policy.py`;
4. `scripts/check_manifest_verifier.py`;
5. `scripts/check_release_packaging_alignment.py`;
6. `scripts/check_release_zip_verifier.py`;
7. `scripts/check_release_safe_extractor.py`;
8. `scripts/check_release_zip_rebuild_from_extract.py`.

Symlink and path-shape checks run before packaging probes so later checks do not accidentally read through non-portable filesystem entries while constructing temporary release ZIPs.

## Operator effect

Maintainers still build and verify releases the same way:

```bash
python3 scripts/release_gate.py
python3 scripts/build_release_zip.py --out ../The-Election-Stack-revNNNN.zip
python3 scripts/verify_release_zip.py ../The-Election-Stack-revNNNN.zip
```

The difference is that ambiguous member names and central-directory byte drift fail before they become a distributable release shape. Direct runs of the release packaging/verifier scripts also suppress Python bytecode-cache writes before importing local helper modules, reducing the chance that a maintainer creates a local `__pycache__` merely by running a packaging diagnostic.

## Compression posture

This revision adds one shared helper, one compact release-gate check, and this maintainer-control document. It does not add external sources, downloaded bodies, schemas, registries, or a new public-answer surface.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/658-release-packaging-scope-alignment-leading-dot-normalization-and-verifier-cli-harness.md`
- `docs/659-release-archive-self-verification-and-single-source-packaging-predicate.md`
- `docs/660-release-zip-canonical-byte-layout-overlay-and-preamble-firewall.md`
- `docs/663-release-zip-permission-canonicalization-and-extraction-rebuild-invariance.md`
- `scripts/release_path_policy.py`
- `scripts/check_release_path_policy.py`
- `scripts/build_manifest.py`
- `scripts/build_release_zip.py`
- `scripts/verify_release_zip.py`
- `scripts/check_release_zip_verifier.py`
- `scripts/check_release_safe_extractor.py`
- `scripts/check_release_zip_rebuild_from_extract.py`

## v791 portable-namespace note

`docs/665-release-portable-path-namespace-and-case-collision-firewall.md` extends the shared path policy from syntactic POSIX safety to portable extraction safety. Release members now also reject reserved Windows device basenames, Windows-forbidden characters, trailing-dot components, overlong policy-bounded names, and case-insensitive namespace collisions.

## v792 extracted-tree manifest note

`docs/667-release-manifest-tree-verifier-and-symlink-safe-hash-closure.md` extends the shared path-policy posture to already extracted trees. `scripts/verify_manifest.py` applies the same release-path and portable-namespace rules to `MANIFEST.sha256` entries and rejects symlink-backed release-scope paths before hashing file bytes.

## v793 safe-extractor note

`docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md` makes the shared path policy directly operator-facing. Instead of relying on a generic extractor and then checking the result, `scripts/extract_release_zip.py` writes each member through `scripts/release_path_policy.py::safe_extract_destination()` into a temporary tree and only renames that tree into place after manifest closure passes.
