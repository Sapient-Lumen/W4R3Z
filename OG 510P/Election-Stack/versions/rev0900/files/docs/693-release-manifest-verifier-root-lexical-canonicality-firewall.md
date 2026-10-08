# 693 — Release manifest verifier root lexical canonicality firewall

**Track:** Shared / Release engineering

This document records a v818 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v817 made manifest member hashing route-aware: both manifest generation and extracted-tree verification reopen member parents and leaves through no-follow routes before accepting bytes. The adjacent extracted-tree verifier root, however, still accepted an operator-supplied root path after `pathlib` / `abspath` normalization had removed purely lexical ambiguity.

That meant these invocations could name the same directory but leave different audit trails:

```text
python3 scripts/verify_manifest.py /release/tree
python3 scripts/verify_manifest.py /release/tree/./child/..
python3 scripts/verify_manifest.py /release//tree/
```

The verifier already rejected symlinked verification roots and symlink-routed ancestry, but it did not fail closed on raw root spellings containing current-directory components, parent-directory components, repeated separators, trailing separators, empty input, or NUL bytes. After the ZIP verifier, safe extractor, and release ZIP builder learned to treat raw carrier paths as evidence-bearing inputs, the extracted-tree verifier needed the same lexical boundary.

## Reconstruction rule

Recipient-side manifest verification now treats the raw verification-root spelling as part of the extracted-tree boundary:

- omitted CLI root means the current working directory as a concrete default;
- explicit empty roots fail;
- NUL-containing roots fail;
- trailing separators fail except for the platform filesystem root spelling;
- repeated separator components fail;
- `.` and `..` components fail before existence, symlink, mode, walk, or hash checks run;
- symlink final roots and symlinked root ancestry remain forbidden by the existing v805 root-anchoring rule.

This keeps root-route auditability aligned with the member-route hardening introduced in v817.

## Enforcement surfaces

v818 updates `scripts/verify_manifest.py` so `verify_tree()` inspects the raw pathlike argument before converting it to an absolute lexical root. The CLI no longer passes a literal `.` for the omitted-root default; it supplies `Path.cwd()` only when the operator omitted the root argument, preserving convenience without normalizing an explicit ambiguous spelling.

v818 extends `scripts/check_manifest_verifier.py` with negative probes for empty, NUL-containing, trailing-separator, current-component, parent-component, and repeated-separator verification roots.

## Operator effect

Normal explicit verification remains:

```text
python3 scripts/verify_manifest.py /path/to/extracted/release
```

Verifying the current working directory without an argument remains supported:

```text
cd /path/to/extracted/release
python3 scripts/verify_manifest.py
```

Ambiguous explicit root spellings now fail closed. Operators should pass the concrete release-tree directory once, without `./`, `../`, repeated separators, or trailing separators.

## Non-claims

This does not add filesystem locking, does not make a mutable extracted tree race-free, and does not claim to authenticate the local path namespace. It closes a narrower ambiguity seam: the verifier must not silently normalize away the route spelling that an operator supplied as the extracted-tree root.

This does not change release ZIP bytes, manifest grammar, schema semantics, voter-facing surfaces, evidence packet semantics, or election-process claims.

## Compression posture

This revision adds one compact release-engineering document and extracted-tree verifier root-path probes. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/692-release-manifest-member-read-canonicality-firewall.md`
- `docs/680-release-extracted-tree-verification-root-anchoring-firewall.md`
- `docs/681-release-safe-extractor-lexical-output-path-canonicality-firewall.md`
- `docs/686-release-zip-input-lexical-path-canonicality-firewall.md`
- `docs/689-release-zip-builder-source-root-canonicality-firewall.md`
- `scripts/verify_manifest.py`
- `scripts/check_manifest_verifier.py`
- `scripts/build_manifest.py`
- `scripts/extract_release_zip.py`
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)
