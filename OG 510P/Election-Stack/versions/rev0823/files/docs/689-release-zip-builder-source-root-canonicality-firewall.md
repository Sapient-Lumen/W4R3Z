# 689 — Release ZIP builder source-root canonicality firewall

**Track:** Shared / Release engineering

This document records a v814 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v809 through v813 tightened release artifact carrier paths on the recipient and publication sides: ZIP verification rejects ambiguous or symlink-routed input paths, safe extraction preserves the verifier's accepted byte snapshot, and release ZIP construction rejects ambiguous or symlink-routed output paths before publishing bytes.

The adjacent construction-side seam was the builder source root. `scripts/build_release_zip.py` accepted `--root`, immediately converted it through `pathlib.Path(...).resolve()`, and then discovered release members under the resolved target. That made the produced member bytes deterministic, but it meant the audit-visible source route could differ from the route actually packaged. Examples include:

```text
--root .
--root repo/./checkout
--root repo//checkout
--root symlink-to-checkout
--root symlink-parent/checkouts/election-stack
```

For release construction, the source tree is evidence-bearing operational context: maintainers should be able to tell which concrete working tree was packaged without relying on shell normalization or filesystem alias resolution.

## Reconstruction rule

Release ZIP construction now treats the source root as an audited input route:

- reject empty source-root paths and NUL-containing source-root paths;
- reject raw source-root spellings with current-directory components, parent-directory components, repeated separator components, or trailing separators;
- reject missing source roots;
- reject source roots that are not directories;
- reject symlink final source-root paths;
- reject symlinked source-root ancestor components;
- keep the accepted source root as an absolute lexical path without resolving symlinks before member discovery.

The CLI default still works, but it no longer passes the literal string `.` into the builder. If no `--root` is supplied, the CLI uses the current working directory as the default concrete root. Operators who pass `--root` explicitly should provide a canonical absolute path or a simple relative directory name without `.`/`..`/repeated separators and without symlink components.

## Enforcement surfaces

v814 updates `scripts/build_release_zip.py` so both in-process `build_zip()` / `release_file_names()` callers and CLI callers share the same source-root preflight. The CLI preserves explicit `--root` strings until the lexical firewall has run; only the omitted default is replaced with the current working directory.

v814 extends `scripts/check_release_builder_filesystem_policy.py` with source-root probes for:

- explicit current-directory components;
- repeated separators;
- trailing separators;
- non-directory source roots;
- symlink final source roots;
- symlink-routed source-root ancestry.

## Operator effect

Canonical usage from the repository root is now:

```text
python3 scripts/build_release_zip.py --out dist/The-Election-Stack-rev0814.zip
```

Explicit root usage remains supported when the path is concrete, for example:

```text
python3 scripts/build_release_zip.py --root /abs/path/to/election-stack --out dist/The-Election-Stack-rev0814.zip
```

Do not pass `--root .`, `--root ./repo`, `--root ../repo`, repeated separators, trailing separators, or symlinked checkout aliases. The builder rejects those before discovering release files or creating output parents.

## Non-claims

This does not make a mutable local checkout a secure build substrate, does not add filesystem locking, and does not claim race-free construction against a privileged local adversary. It closes a maintainer-error and aliasing seam so release construction uses the same concrete-path discipline already applied to verifier input paths, safe-extractor output paths, and builder output paths.

This does not change release ZIP member names, manifest grammar, schema semantics, voter-facing surfaces, evidence packet semantics, or election-process claims.

## Compression posture

This revision adds one compact release-engineering document and builder-source-root regression probes. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/688-release-zip-builder-output-path-canonicality-firewall.md`
- `docs/687-release-safe-extractor-zip-input-snapshot-bridge-firewall.md`
- `docs/686-release-zip-input-lexical-path-canonicality-firewall.md`
- `docs/685-release-zip-single-snapshot-verification-firewall.md`
- `docs/684-release-zip-input-symlink-alias-firewall.md`
- `docs/672-release-builder-byte-exact-manifest-and-file-type-firewall.md`
- `scripts/build_release_zip.py`
- `scripts/check_release_builder_filesystem_policy.py`
- `scripts/verify_release_zip.py`
- `scripts/extract_release_zip.py`
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)
