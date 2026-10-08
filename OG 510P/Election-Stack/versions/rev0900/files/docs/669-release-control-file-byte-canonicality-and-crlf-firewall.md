# 669 — Release control-file byte canonicality and CRLF firewall

**Track:** Shared / Release engineering

This document records a v794 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

By v793 the archive had strong artifact-level and extracted-tree verifiers. The remaining tolerance seam was in the two release control files that bind those verifiers together:

- `VERSION`
- `MANIFEST.sha256`

Earlier verifier paths treated those files as text and, in some places, used tolerant operations such as line splitting or `strip()`. That was convenient, but it meant byte-different control files such as CRLF manifests or `VERSION` values with surrounding whitespace could still be interpreted as semantically equivalent. A release verifier should not silently normalize those bytes. The control files are part of the release surface.

## Reconstruction rule

Release control files are byte-canonical:

1. `VERSION` MUST be exactly one LF-terminated line matching `vNNN\n`.
2. `VERSION` MUST NOT contain CR bytes, leading/trailing spaces, extra blank lines, or multiple records.
3. `MANIFEST.sha256` MUST be UTF-8, LF-only, and final-LF terminated.
4. Each manifest record MUST be exactly `<lowercase-sha256><two spaces><release-path>\n`.
5. Manifest paths MUST pass the shared release path policy.
6. Manifest records MUST be sorted by path and MUST NOT include `MANIFEST.sha256` itself.
7. Duplicate paths and portable namespace collisions MUST fail verification.

These rules intentionally reject control-file forms that many text readers would accept. A recipient should be able to compare verification results without depending on local newline conversion, editor behavior, or platform text-mode habits.

## Enforcement surfaces

v794 adds `scripts/release_control_files.py`, a shared stdlib-only parser for release control-file bytes. The extracted-tree verifier and release-ZIP verifier both use this parser, so `VERSION` and `MANIFEST.sha256` are interpreted the same way before and after extraction.

v794 also adds `scripts/check_release_control_files.py`, a release-gate smoke check that exercises:

- the checked-in `VERSION` bytes;
- the checked-in `MANIFEST.sha256` syntax;
- canonical manifest and version examples;
- CRLF manifest rejection;
- missing-final-newline manifest rejection;
- uppercase-digest manifest rejection;
- blank-line, duplicate-path, and unsorted manifest rejection;
- CRLF, missing-LF, surrounding-whitespace, extra-blank-line, and non-`vNNN` `VERSION` rejection;
- extracted-tree verification rejecting a tree whose manifest or `VERSION` bytes are hash-consistent but not canonical.

The ZIP-artifact verifier smoke check also carries CRLF manifest and CRLF `VERSION` negative probes, so the archive-level verifier cannot regress into tolerant control-file parsing.

## Operator effect

For recipients, no new command is required. Existing verification commands now enforce stricter byte forms:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN.zip
python3 scripts/extract_release_zip.py The-Election-Stack-revNNNN.zip ./election-stack-vNNNN
python3 scripts/verify_manifest.py ./election-stack-vNNNN
```

A tree that differs only by control-file newline conversion is not the same verified release tree. Recreate it from the release ZIP or restore the exact control-file bytes.

For maintainers, the default release ZIP builder now refuses to derive a default output filename from a non-canonical `VERSION` file.

## Non-claims

This is a release-control canonicality guardrail. It does not add cryptographic signing, timestamping, transport security, or source-authentication claims. It prevents permissive local text normalization from changing the verifier's interpretation of the already-sealed release bytes.

## Compression posture

This revision adds one compact maintainer-control document, one shared parser helper, and one small smoke check. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/659-release-archive-self-verification-and-single-source-packaging-predicate.md`
- `docs/667-release-manifest-tree-verifier-and-symlink-safe-hash-closure.md`
- `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`
- `scripts/release_control_files.py`
- `scripts/check_release_control_files.py`
- `scripts/verify_release_zip.py`
- `scripts/verify_manifest.py`
- `scripts/build_release_zip.py`
