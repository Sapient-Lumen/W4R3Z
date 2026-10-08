# 663 — Release ZIP permission canonicalization and extraction-rebuild invariance

**Track:** Shared / Release engineering

This document records a v789 packaging hardening pass discovered during clean extraction testing. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

The deterministic ZIP builder normalized timestamps and entry order, but still derived ZIP permission bits from the local filesystem. That means a local `chmod +x` on a script could change the release ZIP even though `MANIFEST.sha256` did not change, because the manifest seals file bytes, not filesystem mode.

The problem becomes visible when reconstructing from a generic extracted tree. Some ZIP extractors do not preserve executable bits; rebuilding from that extracted tree can produce a byte-different archive even when every file byte still matches the manifest.

For this archive, tools are invoked as explicit Python commands such as `python3 scripts/release_gate.py`. Release correctness does not depend on executable bits in the ZIP.

## Reconstruction rule

`scripts/build_release_zip.py` now stores every release ZIP member as a regular `0644` file. It no longer reads `src_path.stat().st_mode` to decide whether a member should be executable.

`scripts/verify_release_zip.py` now treats `0644` as the canonical release mode. A member with mode `0755`, even if all bytes and hashes match, is a release-shape failure because it makes archive bytes dependent on local filesystem state.

## Extraction-rebuild check

`scripts/check_release_zip_rebuild_from_extract.py` now gates this property directly:

1. build a fresh temporary release ZIP with a fresh manifest;
2. verify that ZIP with `scripts/verify_release_zip.py`;
3. extract it using Python's stdlib `zipfile` extractor;
4. rebuild a release ZIP from the extracted tree;
5. verify the rebuilt ZIP;
6. require the original and rebuilt ZIP byte streams to be identical.

This check specifically catches unsealed metadata drift: permissions, extra fields, comments, member order, layout, or any other ZIP property that can survive outside `MANIFEST.sha256` but still affect archive reproducibility.

## Operator effect

Reconstruction no longer depends on whether an operator used `unzip`, Python `zipfile`, a GUI extractor, or a filesystem that preserves POSIX executable bits. If file bytes are intact and the release builder is used, the ZIP rebuild should be byte-for-byte stable.

## Compression posture

This revision changes the ZIP builder/verifier, adds one compact extraction-rebuild check, and adds this maintainer-control document. It does not add schemas, registries, downloaded external bodies, or a new public-answer surface.

## Internal anchors

- `docs/659-release-archive-self-verification-and-single-source-packaging-predicate.md`
- `docs/660-release-zip-canonical-byte-layout-overlay-and-preamble-firewall.md`
- `scripts/build_release_zip.py`
- `scripts/verify_release_zip.py`
- `scripts/check_release_zip_verifier.py`
- `scripts/check_release_zip_rebuild_from_extract.py`

## v790 extraction-safety note

`docs/664-release-path-policy-safe-extraction-and-central-directory-canonicalization.md` tightens the extraction/rebuild probe by resolving every member destination with `Path.relative_to`-style containment and by sharing the same path policy used by the manifest and ZIP verifier.


## v793 safe-extractor note

`docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md` adds an operator-facing extraction bridge before this rebuild-invariance probe. The safe extractor verifies the ZIP, extracts through the shared path policy, rechecks the extracted manifest, and then publishes the directory; this document's rebuild check remains a separate byte-for-byte reproducibility control.
