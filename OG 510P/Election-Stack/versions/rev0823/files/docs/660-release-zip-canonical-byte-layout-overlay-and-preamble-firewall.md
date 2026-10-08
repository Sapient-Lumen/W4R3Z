# 660 — Release ZIP canonical byte layout, overlay, and preamble firewall

**Track:** Shared / Release engineering

This document records the v788 reconstruction pass for the release ZIP verifier. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

The v787 archive verifier proved member-level integrity: safe names, deterministic metadata, manifest closure, and per-entry SHA-256 agreement against the bytes stored in the ZIP. That still left one archive-only ambiguity: a permissive ZIP reader may accept extra bytes before or after an otherwise valid ZIP payload.

Those extra bytes are not sealed by `MANIFEST.sha256`, are not visible as ZIP members, and can confuse downstream custody narratives. Common examples are a self-extracting preamble before the first local file header or an appended overlay after the end-of-central-directory record. They may be legitimate in other ZIP ecosystems, but they are not a deterministic Election Stack release artifact.

## Reconstruction rule

`scripts/verify_release_zip.py` now treats the ZIP byte stream itself as part of the release shape. A release ZIP must have:

1. the first local file header at byte zero;
2. local file records in the same order as the central directory;
3. no gaps between local file records;
4. no data-descriptor records;
5. no local extra fields;
6. a central directory that starts exactly where the local records end;
7. an end-of-central-directory record that is the final empty-comment record in the file;
8. no prepended preamble, self-extractor stub, appended overlay, or trailing comment bytes.

This is intentionally stricter than generic ZIP compatibility. The release artifact is a canonical evidence container, not an application bundle or a transport wrapper.

## Release-gate probe

`scripts/check_release_zip_verifier.py` still builds a fresh temporary deterministic ZIP and verifies it. The negative probes now include byte-layout mutations as well as member-level mutations:

- manifest hash mismatch;
- duplicate ZIP member;
- unsafe traversal path;
- appended overlay bytes after the EOCD record;
- prepended preamble bytes before the first local file header.

The probe keeps using temporary directories and restores any checked-in manifest bytes it touches, so it remains safe to run before the final `scripts/build_manifest.py --check` or `--write-manifest` step.

## Operator usage

Run the verifier directly on the distributed archive, not only on an extracted tree:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN-*.zip
```

A passing result now means both of these are true:

- every non-manifest ZIP member is sealed by `MANIFEST.sha256` and has the expected digest;
- the raw ZIP stream has no unsealed preamble/overlay material outside the canonical member layout.

## Compression posture

This revision adds one compact maintainer-control document and extends existing stdlib verifier/gate code. It does not add schemas, registries, downloaded external bodies, or a new public-answer surface.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/659-release-archive-self-verification-and-single-source-packaging-predicate.md`
- `scripts/verify_release_zip.py`
- `scripts/check_release_zip_verifier.py`
- `scripts/build_release_zip.py`


## v789 metadata note

`docs/663-release-zip-permission-canonicalization-and-extraction-rebuild-invariance.md` complements this byte-layout firewall by making member permissions canonical `0644` and requiring byte-identical rebuild after stdlib extraction.

## v790 central-directory note

`docs/664-release-path-policy-safe-extraction-and-central-directory-canonicalization.md` complements this byte-layout firewall by parsing central-directory records directly and treating creator-system, version-needed, flags, timestamp words, attributes, sizes, CRCs, and local-header offsets as canonical release bytes.

## v791 portable-namespace note

`docs/665-release-portable-path-namespace-and-case-collision-firewall.md` complements this byte-layout firewall by requiring the canonical member layout to occupy a portable extraction namespace. A byte-canonical ZIP with names that collide after case folding or with Windows-reserved basenames is not a valid release shape.


## v801 stored-member note

`docs/676-release-zip-stored-member-compressor-independent-canonicality.md` complements this byte-layout firewall by making member payload encoding stored rather than deflated, removing compressor-output drift from the canonical archive.

## v795 deflate-stream note

`docs/670-release-zip-deflate-stream-canonicality-and-verifier-rebuild.md` complements this byte-layout firewall by treating the compressed member streams themselves as part of the canonical release bytes. A ZIP with the right local/central-directory shape and the right payload hashes still fails if it is not byte-for-byte equal to the canonical rebuild from those payloads.
