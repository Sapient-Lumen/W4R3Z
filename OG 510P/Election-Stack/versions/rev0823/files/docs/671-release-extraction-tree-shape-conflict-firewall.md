# 671 — Release extraction tree-shape conflict firewall

**Track:** Shared / Release engineering

This document records a v796 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

By v795 the release ZIP verifier checked canonical control-file bytes, portable member names, case-insensitive namespace collisions, local/central-directory layout, canonical permissions, and byte-for-byte ZIP rebuild canonicality. One recipient-side extraction seam remained: an archive could contain individually safe regular-file names that cannot form a portable extracted regular-file tree.

The minimal example is a ZIP containing both:

```text
objects/prefix
objects/prefix/child.json
```

Each member name can be safe in isolation, and `MANIFEST.sha256` can seal both payload bytes. But extraction would require `objects/prefix` to be both a regular file and a directory. The safe extractor already failed this shape when writing the second member; the archive verifier needed to reject it before extraction so recipient commands agree.

## Reconstruction rule

Release members are regular files. Therefore the release path set MUST NOT contain any path that is also a component-prefix of another release path.

For any two release paths `a` and `b`, if `b` starts with `a/`, the set is invalid. This is separate from exact duplicate detection and case-insensitive portable namespace collision detection:

- duplicates answer “would two members write the same file?”;
- portable namespace collisions answer “would two names collide on a common case-insensitive or Windows-style target?”;
- extraction tree-shape conflicts answer “would one member have to be both a file and a directory?”

## Enforcement surfaces

v796 adds `release_path_policy.find_extraction_shape_conflicts()` and uses it in:

- `scripts/release_control_files.py` for `MANIFEST.sha256` parsing;
- `scripts/verify_release_zip.py` for ZIP member-name verification;
- `scripts/verify_manifest.py` for extracted release-scope tree verification;
- `scripts/build_manifest.py` and `scripts/build_release_zip.py` for fail-closed release construction.

The release-gate smoke checks now include shape-conflict probes in:

- `scripts/check_release_path_policy.py`;
- `scripts/check_release_control_files.py`;
- `scripts/check_manifest_verifier.py`;
- `scripts/check_release_zip_verifier.py`.

## Operator effect

Recipient commands are unchanged:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN.zip
python3 scripts/extract_release_zip.py The-Election-Stack-revNNNN.zip ./election-stack-vNNNN
python3 scripts/verify_manifest.py ./election-stack-vNNNN
```

A passing ZIP-verifier result now also means that the archive member set can be represented as a regular-file extraction tree under the release path policy, not merely that every member name is individually safe.

## Non-claims

This does not add signing, timestamping, source authentication, or transport security. It does not change evidence-object schemas or election-process claims. It closes a release-container consistency gap between archive-level verification and recipient extraction.

## Compression posture

This revision adds one compact maintainer-control document and extends existing stdlib helper/verifier checks. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or new jurisdictional claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/664-release-path-policy-safe-extraction-and-central-directory-canonicalization.md`
- `docs/665-release-portable-path-namespace-and-case-collision-firewall.md`
- `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`
- `docs/670-release-zip-deflate-stream-canonicality-and-verifier-rebuild.md`
- `scripts/release_path_policy.py`
- `scripts/release_control_files.py`
- `scripts/verify_release_zip.py`
- `scripts/verify_manifest.py`
- `scripts/build_manifest.py`
- `scripts/build_release_zip.py`
