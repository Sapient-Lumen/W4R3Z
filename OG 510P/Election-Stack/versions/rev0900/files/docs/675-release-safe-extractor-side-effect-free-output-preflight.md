# 675 — Release safe-extractor side-effect-free output preflight

**Track:** Shared / Release engineering

This document records a v800 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

By v799, `scripts/extract_release_zip.py` rejected final output symlinks, symlinked parent components, and lexical `.`/`..` output components. It also repeated the output-ancestry check immediately before publishing a verified extraction tree.

The remaining seam was ordering. The extractor computed a resolved output path and attempted to create the output parent before running the full lexical ancestry firewall. A rejected path could therefore still leave local filesystem side effects, especially when an existing symlink parent was followed during parent-directory creation for a deeper target such as `symlink-parent/new-child/out`.

That is not a payload-integrity failure, but it violates the recipient expectation for a verifier-backed extractor: rejected output targets should fail before creating publication directories.

## Reconstruction rule

Safe extraction must treat output-target preflight as side-effect-free until the operator-supplied path has passed lexical and symlink-ancestry checks:

1. keep the output path lexical until the ancestry firewall has run;
2. reject empty paths and lexical `.`/`..` components before resolving or creating parents;
3. reject existing symlink components before creating any output parent directory;
4. create output parents only after that preflight passes;
5. re-run ordinary output-directory preservation checks after parent creation;
6. repeat output-ancestry checks immediately before final publication.

This keeps invalid output targets from creating new local directories as a side effect of a failed extraction attempt.

## Enforcement surfaces

v800 refactors `scripts/extract_release_zip.py` so `out_root` is a lexical absolute path, not a symlink-resolved path, until after output-target preflight. The extractor now calls the output component firewall before `mkdir(parents=True)` can create the output parent.

v800 also extends `scripts/check_release_safe_extractor.py` with a negative probe for symlinked output ancestry plus a missing child parent. The probe requires the extractor to reject the path and confirms that the symlink target did not receive a newly created directory before rejection.

## Operator effect

The preferred recipient workflow is unchanged:

```bash
python3 scripts/verify_release_zip.py The-Election-Stack-revNNNN.zip
python3 scripts/extract_release_zip.py The-Election-Stack-revNNNN.zip ./election-stack-vNNNN
python3 scripts/verify_manifest.py ./election-stack-vNNNN
```

Choose a direct ordinary output directory. A failed extractor run caused by an unsafe output target should not publish release bytes and should not create redirected parent directories along a rejected symlink route.

## Non-claims

This is a side-effect-ordering hardening for the project-provided stdlib extractor. It does not claim to be a complete hostile-filesystem sandbox, does not eliminate every time-of-check/time-of-use race on every platform, and does not change the archive payload semantics. It narrows the official reconstruction path so ordinary recipient failures are cleaner and less surprising.

## Compression posture

This revision adds one compact release-engineering document and extends an existing smoke test. It does not add schemas, registries, external-source bodies, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`
- `docs/674-release-safe-extractor-output-ancestry-firewall.md`
- `scripts/extract_release_zip.py`
- `scripts/check_release_safe_extractor.py`
- `scripts/verify_release_zip.py`
- `scripts/verify_manifest.py`
