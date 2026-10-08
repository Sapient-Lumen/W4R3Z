# 665 — Release portable path namespace and case-collision firewall

**Track:** Shared / Release engineering

This document records a v791 packaging hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

The v790 release gave manifest, ZIP, verifier, and extraction probes one shared POSIX-style path policy. The next seam was portability after a valid archive leaves the maintainer's POSIX filesystem.

A name can be syntactically safe and still be non-portable. Examples include names that collide on case-insensitive filesystems, names that use Windows device basenames such as `AUX.txt`, and names that contain characters that ordinary Windows filesystems reject even though POSIX accepts them.

None of these shapes were present in v790. The risk was future drift: a release could verify on Linux, then overwrite, fail extraction, or become ambiguous on another operator's platform.

## Reconstruction rule

Release members now occupy a portable namespace, not merely a POSIX namespace.

`scripts/release_path_policy.py` rejects any member path with:

- reserved Windows device basenames, even when an extension is present, such as `CON`, `PRN`, `AUX`, `NUL`, `COM1` through `COM9`, `LPT1` through `LPT9`, `CONIN$`, or `CONOUT$`;
- Windows-forbidden characters: `<`, `>`, `:`, `"`, `|`, `?`, or `*`;
- a component ending in a dot;
- an overlong path or component according to the release policy constants;
- all v790-prohibited traversal, whitespace, control-character, non-ASCII, drive-like, backslash, absolute, and directory-entry shapes.

The archive also rejects case-insensitive namespace collisions. `docs/Example.md` and `docs/example.md` are different POSIX names, but they are the same portable release key and must not coexist in one sealed release.

## Enforcement surfaces

The v791 changes keep the existing single path-policy helper and add portable-namespace checks at the points where whole inventories are visible:

- `scripts/build_manifest.py` fails before writing or checking `MANIFEST.sha256` if the selected release files collide under the portable path key;
- `scripts/build_release_zip.py` fails before writing a ZIP if the selected archive members collide under that same key;
- `scripts/verify_release_zip.py` rejects both exact duplicates and portable ZIP member collisions, and also rejects manifest path collisions;
- `scripts/check_release_path_policy.py` checks the live repository tree plus synthetic bad paths for reserved basenames, forbidden characters, trailing dots, and case-collision behavior;
- `scripts/check_release_zip_verifier.py` includes negative probes for reserved member paths and case-colliding ZIP members.

## Operator effect

Maintainers still use the same commands:

```bash
python3 scripts/release_gate.py
python3 scripts/build_release_zip.py --out ../The-Election-Stack-revNNNN.zip
python3 scripts/verify_release_zip.py ../The-Election-Stack-revNNNN.zip
```

The difference is that a release that is valid only on the maintainer's local filesystem is no longer enough. A deterministic release member name must also be unambiguous for common case-insensitive and Windows-style extraction targets.

## Compression posture

This revision extends existing packaging scripts and adds one compact maintainer-control document. It does not add schemas, registries, external-source bodies, voter-facing surfaces, or a new release-gate child step.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/658-release-packaging-scope-alignment-leading-dot-normalization-and-verifier-cli-harness.md`
- `docs/659-release-archive-self-verification-and-single-source-packaging-predicate.md`
- `docs/660-release-zip-canonical-byte-layout-overlay-and-preamble-firewall.md`
- `docs/663-release-zip-permission-canonicalization-and-extraction-rebuild-invariance.md`
- `docs/664-release-path-policy-safe-extraction-and-central-directory-canonicalization.md`
- `scripts/release_path_policy.py`
- `scripts/build_manifest.py`
- `scripts/build_release_zip.py`
- `scripts/verify_release_zip.py`
- `scripts/check_release_path_policy.py`
- `scripts/check_release_zip_verifier.py`
