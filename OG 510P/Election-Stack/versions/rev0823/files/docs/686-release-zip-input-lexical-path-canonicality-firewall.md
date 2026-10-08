# 686 — Release ZIP input lexical path canonicality firewall

**Track:** Shared / Release engineering

This document records a v811 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v808 made release ZIP filename-version tokens evidence-bearing. v809 then rejected symlink final input paths and symlink-routed input ancestry so those carrier tokens stayed attached to the operator-supplied basename. v810 bound the artifact verdict to a single byte snapshot after that preflight.

One adjacent input-boundary seam remained: the verifier accepted raw path strings that the operating system or `pathlib` can normalize before audit, such as current-directory components, parent-directory components, repeated separators, or a trailing separator. Those spellings do not change a normal immutable artifact, but they weaken the reconstruction story: the verifier report is supposed to describe a concrete artifact path, not a path whose spelling is partly hidden by resolver normalization before symlink and filename-token checks run.

## Reconstruction rule

The release ZIP verifier now treats the operator-supplied input path as a lexical preflight boundary before any filesystem lookup:

- reject an empty input path;
- reject NUL bytes in the raw path string;
- reject trailing separators, because the input must identify one file artifact;
- reject empty separator components such as `//` in the middle of a path;
- reject current-directory and parent-directory components such as `./` and `../` before `pathlib` or the operating system can collapse them;
- only after that lexical check, run the v809 concrete-ancestry check and the v810 single-snapshot read.

This keeps the operator-visible path, filename-token checks, symlink-ancestry checks, and byte-snapshot boundary in one audit sequence.

## Enforcement surfaces

v811 tightens `scripts/verify_release_zip.py` with `_input_path_lexical_problems()`. The CLI now passes the original `argparse` string into `verify_zip()` rather than constructing a `Path` first, preserving raw path spelling long enough for the lexical preflight to see it.

v811 also extends `scripts/check_release_zip_verifier.py` with negative probes for `./`, `../`, `//`, and trailing-separator input spellings that would otherwise resolve to a real candidate archive. These probes sit next to the existing symlink-alias and single-snapshot checks, because all three surfaces describe the same operator-input boundary.

While running the release gate, v811 also made the `scripts/build_manifest.py` status line compatible with Python runtimes that do not allow backslash escapes inside f-string expressions. That is an execution-compatibility fix only; it does not change manifest bytes, manifest scope, or release payload semantics.

## Operator effect

Operator usage remains the same for canonical paths:

```text
python3 scripts/verify_release_zip.py dist/The-Election-Stack-rev0811.zip
```

Operators should pass a direct, concrete file path. These forms now fail before the artifact is read:

```text
python3 scripts/verify_release_zip.py ./dist/The-Election-Stack-rev0811.zip
python3 scripts/verify_release_zip.py dist/tmp/../The-Election-Stack-rev0811.zip
python3 scripts/verify_release_zip.py dist//The-Election-Stack-rev0811.zip
python3 scripts/verify_release_zip.py dist/The-Election-Stack-rev0811.zip/
```

The intent is not convenience normalization; it is audit clarity. A release-verification transcript should preserve the exact carrier path spelling that was checked.

## Non-claims

This does not make mutable local filesystems safe release media, does not add file locking, and does not prove that an artifact path remains unchanged after verification. Those limits remain covered by `docs/685-release-zip-single-snapshot-verification-firewall.md`.

This does not change release ZIP member names, manifest grammar, schema semantics, voter-facing surfaces, evidence packet semantics, or election-process claims.

## Compression posture

This revision adds one compact release-engineering document and a few verifier regression probes. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/685-release-zip-single-snapshot-verification-firewall.md`
- `docs/684-release-zip-input-symlink-alias-firewall.md`
- `docs/683-release-filename-version-token-coherence-firewall.md`
- `scripts/verify_release_zip.py`
- `scripts/check_release_zip_verifier.py`
- `scripts/build_manifest.py`
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)
