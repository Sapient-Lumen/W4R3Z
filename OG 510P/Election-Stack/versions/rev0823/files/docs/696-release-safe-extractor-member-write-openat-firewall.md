# 696 — Release safe-extractor member-write openat firewall

**Track:** Shared / Release engineering

This document records a v821 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v812 bridged safe extraction to the verifier's accepted ZIP byte snapshot, and v817–v820 aligned manifest reads and manifest control-file maintenance with no-symlink route discipline. The adjacent extraction-write path still had a narrower seam: after ZIP verification accepted member names, `scripts/extract_release_zip.py` created member parents with ordinary `Path.mkdir()` and opened member destinations with ordinary `Path.open("xb")`.

That path is safe for well-behaved local filesystems and already rechecks the finished tree before publication, but it leaves the extraction writer less strict than the builder and manifest readers. A local race that swaps a just-created extraction parent directory for a symlink before the leaf file is opened could redirect member bytes outside the temporary extraction tree, even though final publication would later fail. The extractor should avoid redirected writes, not merely avoid publishing the redirected tree.

## Reconstruction rule

Safe extraction now treats member writes as a concrete route boundary:

- each ZIP member name is rechecked against the shared release path policy immediately before writing;
- extraction creates or opens each member parent component through directory descriptors where the platform supports `dir_fd` and `O_NOFOLLOW`;
- existing extraction directories must open as directories without following symlinks;
- member leaf files are created with exclusive create and `O_NOFOLLOW` where available;
- created member leaves must be regular files before bytes are copied;
- the temporary extraction root is kept as an absolute lexical path rather than a symlink-resolved path.

The extractor still verifies the ZIP before writing, extracts from the verifier's accepted byte snapshot, canonicalizes directory modes, verifies the extracted manifest tree, and publishes the temporary tree only after those checks pass.

## Enforcement surfaces

v821 updates `scripts/extract_release_zip.py` with no-follow member destination helpers for extraction-directory creation and leaf-file creation. The helper closes the post-verification member-write gap without changing ZIP member grammar or release path syntax.

v821 extends `scripts/check_release_safe_extractor.py` with a symlink-swap probe that replaces a just-created extraction member directory with a symlink during extraction. The probe must fail closed and must not write any release member bytes into the symlink target.

## Operator effect

Normal recipient use remains:

```text
python3 scripts/extract_release_zip.py dist/The-Election-Stack_<VERSION>.zip election-stack-<VERSION>
```

The difference is fail-closed behavior during extraction if an extraction directory component is swapped to a symlink or otherwise stops being an ordinary directory before a member leaf is created. The tool reports the extraction failure, removes the temporary tree, and does not publish an output directory.

## Non-claims

This does not add OS-level sandboxing, repository locking, filesystem namespaces, or defenses against every possible local privileged actor. It closes the narrower member-write seam: verifier-backed extraction must not follow symlinked extraction-directory components or leaf destinations while copying accepted member bytes.

This does not change election-process claims, evidence packet semantics, schema semantics, release member names, manifest grammar, ZIP byte canonicality, or output-directory clean/replace consent rules.

## Compression posture

This revision adds one compact release-engineering document and a bounded smoke probe. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/695-release-manifest-control-file-read-write-canonicality-firewall.md`
- `docs/692-release-manifest-member-read-canonicality-firewall.md`
- `docs/687-release-safe-extractor-zip-input-snapshot-bridge-firewall.md`
- `docs/681-release-safe-extractor-lexical-output-path-canonicality-firewall.md`
- `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`
- `scripts/extract_release_zip.py`
- `scripts/check_release_safe_extractor.py`
- `scripts/verify_release_zip.py`
- `scripts/verify_manifest.py`
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)
