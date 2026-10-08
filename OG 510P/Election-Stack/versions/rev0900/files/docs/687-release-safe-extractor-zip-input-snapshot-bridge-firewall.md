# 687 — Release safe-extractor ZIP input snapshot bridge firewall

**Track:** Shared / Release engineering

This document records a v812 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v809 made `scripts/verify_release_zip.py` reject symlink final input paths and symlink-routed ZIP input ancestry. v810 then made the ZIP verifier read the artifact once into a single byte snapshot. v811 added a raw lexical input-path preflight so `./`, `../`, repeated separators, and trailing separators cannot be normalized away before that verifier boundary.

One adjacent bridge remained in the operator-facing extractor. `scripts/extract_release_zip.py` called the hardened verifier, but it first resolved the ZIP path before verification and then reopened the ZIP path from disk for extraction after verification succeeded. That created two reconstruction risks:

- resolving the input path could erase the raw carrier-path spelling that the verifier is supposed to audit;
- reopening the path for extraction could make the extracted tree come from a different byte stream than the one whose hash, layout, manifest, and canonical rebuild checks passed.

The normal release lane uses immutable local artifacts, but the extractor should still be internally coherent: the bytes it publishes must be the exact bytes the verifier accepted.

## Reconstruction rule

The safe extractor now treats the release ZIP input as a verifier-owned byte boundary:

- pass the raw operator-supplied ZIP path string into `verify_release_zip.verify_zip()`;
- do not call `Path.resolve()` on the ZIP input before the verifier's lexical, symlink-ancestry, filename-token, and snapshot checks;
- keep the CLI path raw as well, rather than wrapping `args.zip` in `Path()` before calling the extractor API;
- expose the verified byte snapshot on the verifier result for trusted in-process consumers;
- extract from `io.BytesIO(zip_result.zip_bytes)` after a successful verifier result, not by reopening the filesystem path.

This makes the safe extractor a true bridge from artifact verification to publication: the published tree is derived from the same byte snapshot whose SHA-256 and canonical ZIP shape were checked.

## Enforcement surfaces

v812 updates `scripts/verify_release_zip.py` so successful `VerifyResult` objects carry the accepted ZIP snapshot in a non-printing `zip_bytes` field. The CLI JSON and human output remain unchanged; the snapshot is only an in-process handoff for tools such as the safe extractor.

v812 updates `scripts/extract_release_zip.py` so both API and CLI callers preserve the raw ZIP input path until the verifier sees it, and so extraction uses the verifier snapshot through `io.BytesIO`.

v812 extends `scripts/check_release_safe_extractor.py` with probes that require:

- lexically ambiguous ZIP input paths to fail before output creation;
- symlink ZIP input aliases to fail before output creation;
- the extractor CLI to preserve raw ZIP input spelling, not normalize it through `Path(args.zip)`;
- extraction to continue from the verifier snapshot even if the filesystem path is mutated immediately after verification returns.

## Operator effect

Canonical usage is unchanged:

```text
python3 scripts/extract_release_zip.py dist/The-Election-Stack-rev0812.zip /tmp/election-stack-v812
```

Operators should pass a direct, concrete ZIP file path. The same raw-input rules that apply to `scripts/verify_release_zip.py` now apply through the safe extractor as well. For example, these fail before extraction writes an output tree:

```text
python3 scripts/extract_release_zip.py ./dist/The-Election-Stack-rev0812.zip /tmp/election-stack-v812
python3 scripts/extract_release_zip.py dist/tmp/../The-Election-Stack-rev0812.zip /tmp/election-stack-v812
python3 scripts/extract_release_zip.py dist//The-Election-Stack-rev0812.zip /tmp/election-stack-v812
```

The extracted files now come from the verifier's accepted byte snapshot. The reported `zip_sha256` remains the hash of that snapshot.

## Non-claims

This does not make mutable local filesystems safe release media, does not introduce file locking, and does not prove that an artifact path remains unchanged after extraction. It only ensures that a single safe-extractor invocation does not verify one ZIP byte stream and publish another.

This does not change release ZIP member names, manifest grammar, schema semantics, voter-facing surfaces, evidence packet semantics, or election-process claims.

## Compression posture

This revision adds one compact release-engineering document and a few safe-extractor regression probes. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/686-release-zip-input-lexical-path-canonicality-firewall.md`
- `docs/685-release-zip-single-snapshot-verification-firewall.md`
- `docs/684-release-zip-input-symlink-alias-firewall.md`
- `docs/681-release-safe-extractor-lexical-output-path-canonicality-firewall.md`
- `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`
- `scripts/verify_release_zip.py`
- `scripts/extract_release_zip.py`
- `scripts/check_release_safe_extractor.py`
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)
