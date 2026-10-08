# 688 — Release ZIP builder output-path canonicality firewall

**Track:** Shared / Release engineering

This document records a v813 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v809 through v812 tightened the recipient side of release ZIP handling: the verifier rejects symlinked or lexically ambiguous ZIP input paths, reads one byte snapshot, and the safe extractor publishes only from that accepted snapshot.

The adjacent construction-side seam was the release ZIP builder output path. `scripts/build_release_zip.py` produced canonical archive bytes, but its `--out` route was still more permissive than the verifier and extractor routes that later consume the artifact. A maintainer could ask the builder to write through a path spelling or filesystem route that the recipient-side tools would reject, such as:

```text
./dist/../dist/The-Election-Stack-rev0813.zip
dist//The-Election-Stack-rev0813.zip
symlink-parent/The-Election-Stack-rev0813.zip
symlink-output.zip
```

That did not change the ZIP member bytes, but it left release creation with a weaker carrier-path boundary than release verification. The builder should not create an official artifact through an output path that the verifier or safe extractor would later treat as ambiguous evidence.

## Reconstruction rule

Release ZIP construction now treats the builder output path as an artifact-publication route:

- reject empty output paths and NUL-containing output paths;
- reject raw output spellings with current-directory components, parent-directory components, repeated separator components, or trailing separators;
- reject existing symlink final output paths;
- reject existing symlink components in the output ancestry;
- reject existing non-regular final output paths;
- create missing concrete parent directories only after the lexical/symlink route preflight passes;
- write ZIP bytes into a temporary sibling file, then recheck the output route immediately before the final replacement.

The builder still permits an existing ordinary output file to be replaced, and it still permits first-time creation under a concrete parent path. The default `dist/` output lane remains local-only and excluded from the release manifest.

## Enforcement surfaces

v813 updates `scripts/build_release_zip.py` so both CLI and in-process callers use the same output-route preflight. The CLI preserves the raw `--out` string until the lexical check has run, rather than constructing a `Path` that can normalize away `./` components before audit.

The builder now writes the candidate ZIP into a temporary sibling and publishes it with `os.replace()` only after a second output-route check. This keeps a final-path symlink swap between ZIP byte generation and publication from being followed silently.

v813 extends `scripts/check_release_builder_filesystem_policy.py` with probes for:

- lexically ambiguous builder output paths;
- repeated-separator output paths;
- existing directory outputs;
- symlink final output paths;
- symlinked output parent components;
- final-path symlink mutation immediately before publication;
- cleanup of temporary ZIP files after a publish rejection.

## Operator effect

Canonical usage from the repository root is now:

```text
python3 scripts/build_release_zip.py --out dist/The-Election-Stack-rev0814.zip
```

Do not use output paths that depend on shell normalization, parent traversal, repeated separators, symlinked publication directories, or symlinked final filenames. As of v814, omit `--root` from the checkout root or provide a concrete non-symlinked source root; do not pass `--root .`. The builder rejects those before creating release bytes or publication parents.

## Non-claims

This does not make mutable local filesystems a secure build substrate, does not add file locking, and does not claim race-free publication against a privileged local adversary. It narrows the maintainer-error and local-alias seam so the official builder, verifier, and safe extractor share the same concrete-path discipline.

This does not change release ZIP member names, manifest grammar, schema semantics, voter-facing surfaces, evidence packet semantics, or election-process claims.

## Compression posture

This revision adds one compact release-engineering document and builder-output regression probes. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/687-release-safe-extractor-zip-input-snapshot-bridge-firewall.md`
- `docs/686-release-zip-input-lexical-path-canonicality-firewall.md`
- `docs/685-release-zip-single-snapshot-verification-firewall.md`
- `docs/684-release-zip-input-symlink-alias-firewall.md`
- `docs/672-release-builder-byte-exact-manifest-and-file-type-firewall.md`
- `scripts/build_release_zip.py`
- `scripts/check_release_builder_filesystem_policy.py`
- `scripts/verify_release_zip.py`
- `scripts/extract_release_zip.py`
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)
