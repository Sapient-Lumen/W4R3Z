# 667 — Release manifest tree verifier and symlink-safe hash closure

**Track:** Shared / Release engineering

This document records a v792 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

The release ZIP verifier checks the canonical archive bytes before extraction. That is the strongest artifact-level proof, but downstream reviewers often receive or inspect an already extracted tree. In that mode, `MANIFEST.sha256` still exists, but the archive did not previously ship a dedicated extracted-tree verifier with the same strict posture as the ZIP verifier.

The practical seam was not that v791 contained a bad manifest. It did not. The seam was reconstruction workflow drift:

- a reviewer could check individual hashes but miss an extra release-scope file;
- a malformed or duplicate manifest line could be interpreted inconsistently by ad hoc tooling;
- a symlink could make a manifest entry depend on local filesystem state instead of release bytes;
- the portable path namespace enforced for ZIP members needed an extracted-tree counterpart.

## Reconstruction rule

An extracted release tree is valid only when `MANIFEST.sha256` is a strict closure over ordinary release files.

The extracted-tree verifier must check:

1. `MANIFEST.sha256` is present, UTF-8, newline-terminated, sorted, and uses exactly `<lowercase sha256><two spaces><release path>` lines;
2. the manifest does not hash itself;
3. every manifest path satisfies the shared release path policy in `scripts/release_path_policy.py`;
4. manifest paths do not collide in the portable, case-insensitive release namespace;
5. every manifest entry exists in the extracted tree as a regular file, not a symlink;
6. every release-scope regular file selected by `scripts/build_manifest.py` appears in the manifest;
7. every listed file's SHA-256 digest matches the manifest.

## Enforcement surfaces

v792 adds `scripts/verify_manifest.py`, a stdlib-only verifier for extracted release trees. It is intentionally parallel to `scripts/verify_release_zip.py`, but it operates after extraction and does not require the original ZIP bytes.

v792 also adds `scripts/check_manifest_verifier.py`, which runs in the release gate. The check verifies the live tree under a freshly computed manifest, restores the checked-in manifest bytes, and then exercises synthetic negative probes for:

- hash mismatch;
- missing listed files;
- unlisted release-scope files;
- unsafe manifest paths;
- duplicate manifest paths;
- portable case-collision paths;
- release-scope symlink files, when the platform supports symlink creation.

The canonical release-gate inventory runs this check before ZIP packaging probes so tree closure failures are localized before archive-byte checks.

## Operator effect

For a full archive, use the ZIP verifier before extraction:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN.zip
```

For an already extracted tree, use the manifest verifier:

```bash
python3 scripts/verify_manifest.py /path/to/extracted/tree
```

A passing extracted-tree check does not prove the original ZIP byte layout was canonical; it proves the extracted release files are exactly the files sealed by `MANIFEST.sha256`, under the shared release path and portable namespace policy.

## Compression posture

This revision adds one compact maintainer-control document and two small stdlib scripts. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/658-release-packaging-scope-alignment-leading-dot-normalization-and-verifier-cli-harness.md`
- `docs/659-release-archive-self-verification-and-single-source-packaging-predicate.md`
- `docs/663-release-zip-permission-canonicalization-and-extraction-rebuild-invariance.md`
- `docs/664-release-path-policy-safe-extraction-and-central-directory-canonicalization.md`
- `docs/665-release-portable-path-namespace-and-case-collision-firewall.md`
- `scripts/verify_manifest.py`
- `scripts/check_manifest_verifier.py`
- `scripts/build_manifest.py`
- `scripts/release_path_policy.py`

## v793 safe-extractor note

`docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md` connects the ZIP verifier to this extracted-tree verifier. The safe extractor invokes `scripts/verify_manifest.py` on the temporary extraction output before publishing the final directory, so a recipient can make extraction itself part of the verification workflow instead of running the tree check only after a generic unpack step.
