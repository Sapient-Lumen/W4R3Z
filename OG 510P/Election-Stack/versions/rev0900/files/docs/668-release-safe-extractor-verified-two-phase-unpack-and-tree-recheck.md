# 668 — Release safe extractor, verified two-phase unpack, and tree recheck

**Track:** Shared / Release engineering

This document records a v793 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

By v792 the archive had two strong verification surfaces:

- `scripts/verify_release_zip.py` verifies the canonical ZIP artifact before extraction.
- `scripts/verify_manifest.py` verifies an already extracted tree against `MANIFEST.sha256`.

The remaining workflow seam was the step between those two states. A recipient could still run a generic extractor, an old GUI unzipper, or custom `extractall()` wrapper and only later discover that output clobbering, path-policy drift, or partial extraction had happened. The archive verifier and tree verifier were correct, but the project did not yet ship an official bridge that made safe extraction itself part of the release discipline.

## Reconstruction rule

A release ZIP should be unpacked through a verify-first, publish-last extractor:

1. verify the ZIP bytes with the canonical release ZIP verifier;
2. write members one by one through the shared release path policy;
3. write into a temporary sibling directory, not directly into the final output directory;
4. set canonical file permissions on extracted files;
5. verify the temporary extracted tree against `MANIFEST.sha256`;
6. rename the verified temporary tree into place only after all checks pass;
7. refuse to overwrite a non-empty output directory unless an explicit clean replacement was requested;
8. reject symlink output roots rather than following or replacing them.

This rule does not replace independent ZIP verification. It operationalizes it for the common recipient task: turning a release ZIP into a local tree without relying on extractor-specific path or overwrite behavior.

## Enforcement surfaces

v793 adds `scripts/extract_release_zip.py`, a stdlib-only safe extractor. It imports the existing ZIP and manifest verifiers instead of copying their policies. Its default behavior is conservative: a bad ZIP is not extracted, and an existing non-empty output directory is not changed.

v793 also adds `scripts/check_release_safe_extractor.py`, a release-gate smoke check. The check builds a fresh deterministic release ZIP under a temporary manifest, extracts it through the safe extractor, verifies the resulting tree, and exercises negative probes for:

- bad ZIP rejected before extraction;
- non-empty output directory preserved without clean replacement;
- explicit clean replacement removing stale local files;
- output symlink rejection when the platform supports symlinks.

The canonical release-gate inventory runs the safe-extractor smoke check after the ZIP verifier probe and before extraction-rebuild invariance. That order keeps failures localized: archive-byte validity first, operator extraction behavior second, rebuild invariance third.

## Operator effect

For a release archive:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN.zip
python3 scripts/extract_release_zip.py The-Election-Stack-revNNNN.zip ./election-stack-vNNNN
python3 scripts/verify_manifest.py ./election-stack-vNNNN
```

The middle command already performs both verifier calls. The surrounding commands remain useful when an operator wants explicit before/after evidence in a transcript.

To replace a known local extraction directory after the ZIP verifies:

```bash
python3 scripts/extract_release_zip.py The-Election-Stack-revNNNN.zip ./election-stack-vNNNN --clean
```

Use `--clean` only for a deliberate local replacement. It is not needed for a new output directory.

## Non-claims

This extractor is a release-engineering guardrail. It does not claim to be a forensic filesystem tool, a sandbox, a malware scanner, or a substitute for reviewing the release contents. It reduces avoidable extraction ambiguity by binding unpacking to the archive's existing deterministic ZIP and manifest policies.

## Compression posture

This revision adds one compact maintainer-control document and two small stdlib scripts. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/659-release-archive-self-verification-and-single-source-packaging-predicate.md`
- `docs/663-release-zip-permission-canonicalization-and-extraction-rebuild-invariance.md`
- `docs/664-release-path-policy-safe-extraction-and-central-directory-canonicalization.md`
- `docs/667-release-manifest-tree-verifier-and-symlink-safe-hash-closure.md`
- `scripts/extract_release_zip.py`
- `scripts/check_release_safe_extractor.py`
- `scripts/verify_release_zip.py`
- `scripts/verify_manifest.py`
- `scripts/release_path_policy.py`
