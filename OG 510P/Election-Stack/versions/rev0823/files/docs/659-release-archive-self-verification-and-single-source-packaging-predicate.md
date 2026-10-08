# 659 — Release archive self-verification and single-source packaging predicate

**Track:** Shared / Release engineering

This document records the v787 reconstruction pass for ZIP-artifact verification. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

The v786 release made manifest scope and deterministic ZIP scope a release-gate invariant, but the release artifact itself still lacked a first-class verifier. A maintainer could validate an extracted tree with `scripts/build_manifest.py --check` and still miss archive-only faults such as duplicate ZIP members, unsafe traversal names, non-normalized timestamps or permissions, stale filename/version wiring, or a ZIP member that is not sealed by the in-archive manifest.

A second residual issue remained in the packaging code: `scripts/build_release_zip.py` and `scripts/build_manifest.py` were aligned by a drift check, but the ZIP builder still carried its own include predicate. That kept the release safe under the gate, but it left needless duplication in the code path that decides what ships.

## Reconstruction rule

`scripts/verify_release_zip.py` is now the archive-artifact verifier. It verifies a ZIP without extracting it and requires:

1. unique, sorted, traversal-safe member names;
2. fixed deterministic timestamps, stored entries, empty ZIP extra fields/comments, and normalized file modes;
3. `VERSION` and `MANIFEST.sha256` entries;
4. optional filename/version agreement when the ZIP name carries a `revNNNN` or `_vNNN` version marker;
5. `MANIFEST.sha256` closure over every non-manifest ZIP entry;
6. per-entry SHA-256 agreement against the bytes inside the ZIP;
7. byte-for-byte canonical rebuild from the sealed member payload bytes.

This complements, rather than replaces, the extracted-tree checks. The tree checks prove the repository content is coherent; the archive verifier proves the distributed ZIP carries exactly the sealed content in deterministic form.

## Release-gate probe

`scripts/check_release_zip_verifier.py` is now a release-gate child step. It builds a temporary deterministic ZIP using a freshly computed manifest, verifies that the archive-artifact verifier accepts it, and then runs small negative probes that must fail:

- a manifest hash mismatch;
- a duplicate ZIP member;
- an unsafe traversal path;
- a whitespace-bearing member path;
- a reserved portable member name;
- a case-insensitive portable namespace collision;
- a noncanonical file mode;
- appended overlay bytes;
- prepended preamble/self-extractor bytes.

The smoke check temporarily writes the freshly computed manifest only while building the probe ZIP and restores the working tree afterward. That keeps `scripts/release_gate.py --write-manifest` usable: the verifier smoke test does not require the checked-in manifest to already be refreshed before the final manifest-write step runs.

## Single-source packaging predicate

`scripts/build_release_zip.py` now treats `scripts/build_manifest.py::should_include_rel()` as the single source of truth for release payload scope. The only intentional difference is `MANIFEST.sha256` itself: the manifest does not hash itself, while the ZIP must include it.

The existing packaging-alignment gate remains useful as a firewall and regression test. It now verifies that the single-source predicate wiring is preserved and that known local-only paths continue to be excluded.

## Operator usage

After building a release archive, verify the ZIP artifact directly:

```bash
python3 scripts/verify_release_zip.py dist/The-Election-Stack_<VERSION>.zip
```

The verifier prints the archive version, ZIP entry count, manifest entry count, and archive SHA-256 on success. Use `--json` when a downstream CI lane needs a machine-readable result.

## Compression posture

This revision adds one compact maintainer-control document and one stdlib-only artifact verifier plus its gate smoke test. It does not add schemas, registries, downloaded bodies, external sources, or a new public-answer surface.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/658-release-packaging-scope-alignment-leading-dot-normalization-and-verifier-cli-harness.md`
- `scripts/build_manifest.py`
- `scripts/build_release_zip.py`
- `scripts/check_release_packaging_alignment.py`
- `scripts/verify_release_zip.py`
- `scripts/check_release_zip_verifier.py`


## v789 extraction-rebuild note

`docs/663-release-zip-permission-canonicalization-and-extraction-rebuild-invariance.md` tightens this rule: local filesystem executable bits are not release evidence, so the ZIP builder stores every member as `0644` and the gate checks byte-identical rebuild after stdlib extraction.

## v790 path-policy note

`docs/664-release-path-policy-safe-extraction-and-central-directory-canonicalization.md` tightens this archive-verification surface: manifest, ZIP, verifier, and extraction probes now share one release-path policy, and the ZIP verifier parses central-directory metadata directly instead of relying only on the `zipfile` projection.

## v791 portable-namespace note

`docs/665-release-portable-path-namespace-and-case-collision-firewall.md` tightens the archive-verification surface again: the verifier now rejects reserved/forbidden portable member names and case-insensitive member collisions, not merely exact duplicate ZIP names.

## v792 extracted-tree verifier note

`docs/667-release-manifest-tree-verifier-and-symlink-safe-hash-closure.md` adds the extracted-tree counterpart to the ZIP verifier. `scripts/verify_release_zip.py` remains the artifact-byte verifier for a ZIP; `scripts/verify_manifest.py` verifies an already unpacked tree against strict `MANIFEST.sha256` syntax, path policy, portable namespace uniqueness, regular-file closure, and per-file hashes.

## v793 safe-extractor note

`docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md` adds the operator-facing bridge from archive-byte verification to extracted-tree verification. `scripts/extract_release_zip.py` verifies the ZIP with this document's verifier before writing any release member, then verifies the extracted temporary tree with `scripts/verify_manifest.py` before publishing it.


## v801 stored-member note

`docs/676-release-zip-stored-member-compressor-independent-canonicality.md` tightens this surface by requiring release ZIP members to use `ZIP_STORED`; the verifier rejects deflated entries and still compares a canonical rebuild byte-for-byte against the distributed archive.

## v795 deflate-stream canonicality note

`docs/670-release-zip-deflate-stream-canonicality-and-verifier-rebuild.md` tightens this verifier surface again: after member hashes and raw ZIP layout pass, `scripts/verify_release_zip.py` rebuilds the canonical ZIP byte stream from the sealed member payloads and rejects archives whose compressed bytes or other raw archive bytes differ from that canonical rebuild.
