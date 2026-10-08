# 672 — Release builder byte-exact manifest and file-type firewall

**Track:** Shared / Release engineering

This document records a v797 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

By v796, recipient-side verification rejected non-canonical control files, unsafe paths, symlinks, special files, case collisions, file/directory extraction-shape conflicts, and noncanonical ZIP byte streams. The remaining seam was on the maintainer construction side:

- `scripts/build_manifest.py --check` compared `MANIFEST.sha256` through text-mode reads, which can normalize CRLF to LF on some platforms and mask control-file byte drift;
- manifest writing also used text mode, leaving newline encoding to the host runtime rather than the release policy;
- the manifest and ZIP builders relied on separate hygiene checks to catch symlinks, even though `Path.is_file()` follows symlinks by default.

The archive did not contain those bad shapes. The risk was reconstruction drift: a maintainer could run a narrower builder command and get a tolerant result even though the verifier side had become byte-strict.

## Reconstruction rule

Release construction must use the same fail-closed posture as release verification:

1. `MANIFEST.sha256` generation writes exact UTF-8 LF-only bytes, not host text-mode newline output;
2. `build_manifest.py --check` compares raw bytes, not text-normalized strings;
3. release-scope symlinks are rejected by builders before hashing or packaging;
4. release-scope non-regular filesystem nodes are rejected by builders before hashing or packaging;
5. manifest entry formatting remains centralized through `scripts/release_control_files.py` so parser and writer canonicality do not drift.

## Enforcement surfaces

v797 refactors `scripts/build_manifest.py` to expose byte-first helper functions:

- `build_manifest_entries()`
- `build_manifest_text()`
- `build_manifest_bytes()`
- `check_manifest_bytes()`

The check/write CLI now uses `Path.read_bytes()` and `Path.write_bytes()` so CRLF conversion cannot be hidden by Python text I/O.

v797 also tightens `scripts/build_release_zip.py` so file selection rejects symlinks and non-regular release-scope paths before opening member bytes.

`check_release_builder_filesystem_policy.py` is added to the release gate. It verifies that:

- a CRLF-normalized otherwise-current manifest is rejected by the manifest checker;
- a release-scope symlink is rejected by both the manifest builder and ZIP builder;
- a release-scope FIFO/special file is rejected by both builders on platforms that support creating one.

## Operator effect

Maintainer commands are unchanged:

```bash
python3 scripts/build_manifest.py --check
python3 scripts/build_manifest.py
python3 scripts/build_release_zip.py
```

The difference is that these commands now behave like the verifier side: byte drift and filesystem-node ambiguity are construction failures, not artifacts to be caught only by a later full release gate.

## Non-claims

This is a release-construction guardrail. It does not add signing, timestamping, sandboxing, source authentication, or transport security. It does not change evidence-object semantics or election-process claims.

## Compression posture

This revision adds one compact maintainer-control document and one small stdlib smoke check. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or new jurisdictional claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/667-release-manifest-tree-verifier-and-symlink-safe-hash-closure.md`
- `docs/669-release-control-file-byte-canonicality-and-crlf-firewall.md`
- `docs/671-release-extraction-tree-shape-conflict-firewall.md`
- `scripts/build_manifest.py`
- `scripts/build_release_zip.py`
- `scripts/check_release_builder_filesystem_policy.py`
- `scripts/release_control_files.py`
