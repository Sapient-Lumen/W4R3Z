# 674 — Release safe-extractor output ancestry firewall

**Track:** Shared / Release engineering

This document records a v799 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

By v793, `scripts/extract_release_zip.py` verified the release ZIP before writing, extracted through the shared release path policy into a temporary sibling tree, rechecked `MANIFEST.sha256`, and only then published the verified output directory. It also rejected a final output directory that was itself a symlink.

The remaining recipient-side seam was output ancestry. A path such as `symlink-parent/out` can have a safe-looking final component while an existing parent component is a symlink. If the extractor resolves that path before publishing, the verified tree may be redirected into the symlink target. That is not a release-member path traversal problem, and it is not visible to the ZIP verifier; it is an output-target publication problem.

## Reconstruction rule

Safe extraction must treat the operator-supplied output path as part of the publication surface:

1. inspect the lexical output path before resolving symlinks;
2. reject empty output paths;
3. reject lexical `.` or `..` components in the output target;
4. reject any existing symlink component in the output ancestry, not just the final output directory;
5. perform the same ancestry check again immediately before replacing an empty or explicitly clean output directory;
6. continue preserving non-empty outputs unless `--clean` is explicit.

This rule keeps verified bytes from being published through an ambiguous local filesystem route. It is intentionally stricter than generic unzip tools because the project ships a verifier-backed extractor for release reconstruction.

## Enforcement surfaces

v799 extends `scripts/extract_release_zip.py` with an output-target component firewall. The helper inspects the operator-supplied path lexically, without using `Path.resolve()` as the first step, so an existing symlink parent cannot be hidden by resolution. The same helper is used during preflight and again immediately before final publication.

v799 also extends `scripts/check_release_safe_extractor.py` with negative probes for:

- final output symlink rejection;
- symlinked parent-component rejection;
- lexical parent-traversal rejection;
- preservation of existing non-empty output directories without explicit `--clean`.

The release-gate inventory continues to run the safe-extractor smoke check after ZIP verification and before extraction/rebuild invariance.

## Operator effect

Preferred recipient workflow remains:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN.zip
python3 scripts/extract_release_zip.py The-Election-Stack-revNNNN.zip ./election-stack-vNNNN
python3 scripts/verify_manifest.py ./election-stack-vNNNN
```

Choose a direct, ordinary output directory. Avoid symlinked parent paths and `..` components. If replacing an existing extraction, use `--clean` only with a deliberately chosen non-symlink directory.

## Non-claims

This is a local publication guardrail for the shipped safe extractor. It does not claim to prevent every filesystem race on every operating system, implement a sandbox, audit mount namespaces, or make generic external unzip tools safe. It narrows the official extraction path so normal reconstruction does not follow symlinked output ancestry.

## Compression posture

This revision adds one compact maintainer-control document and extends an existing stdlib smoke check. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`
- `docs/664-release-path-policy-safe-extraction-and-central-directory-canonicalization.md`
- `scripts/extract_release_zip.py`
- `scripts/check_release_safe_extractor.py`
- `scripts/verify_release_zip.py`
- `scripts/verify_manifest.py`
