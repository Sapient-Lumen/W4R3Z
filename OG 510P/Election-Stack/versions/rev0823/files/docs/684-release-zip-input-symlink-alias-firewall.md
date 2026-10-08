# 684 — Release ZIP input symlink alias firewall

**Track:** Shared / Release engineering

This document records a v809 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v808 made release ZIP filename version tokens evidence-bearing carrier metadata. That closed conflicting names such as `rev0808-v807`, but one alias seam remained: `scripts/verify_release_zip.py` resolved the input path before inspecting filename tokens.

That means a local operator could invoke the verifier through a symlink whose visible basename carried a stale or conflicting release claim while the resolved target had a clean name. The ZIP payload would still be byte-canonical, but the verifier would report success on the target artifact while ignoring the operator-supplied carrier name.

A symlinked parent directory creates the same class of ambiguity. The visible path may appear to live under one local publication lane while the bytes are read from another.

## Reconstruction rule

The release ZIP verifier now treats its input path as part of the artifact verification boundary:

- the final input path component must be a concrete regular file, not a symlink;
- existing input-path ancestors must not be symlink components;
- filename version-token checks use the operator-supplied basename, not a post-resolution target basename;
- the ZIP bytes are read only after the symlink path preflight has passed.

This keeps the carrier-name rule from v808 meaningful. A release artifact may be copied or hard-linked under a new local filename, but the visible filename presented to the verifier is the filename whose version tokens are checked. Symlink aliases are not accepted as release artifacts.

## Enforcement surfaces

v809 tightens `scripts/verify_release_zip.py` by adding a pre-open input-path preflight. The preflight uses lexical absolute paths rather than `Path.resolve()` so symlink components are detected instead of normalized away.

v809 also extends `scripts/check_release_zip_verifier.py` with two negative probes where symlinks are supported by the local filesystem:

- a stale-version symlink basename pointing at a valid release ZIP must fail before archive verification;
- a valid release ZIP reached through a symlinked parent directory must fail before archive verification.

The existing filename-token probes remain in place, so `rev0809-v809` stays valid while `rev0809-v808` and padded semantic `v0809` forms stay invalid.

## Operator effect

Verify the concrete release ZIP file directly:

```text
python3 scripts/verify_release_zip.py dist/The-Election-Stack-rev0809.zip
```

Do not verify through local symlink aliases such as:

```text
latest.zip -> The-Election-Stack-rev0809.zip
The-Election-Stack-rev0808.zip -> The-Election-Stack-rev0809.zip
linked-dist/The-Election-Stack-rev0809.zip -> real-dist/The-Election-Stack-rev0809.zip
```

If a mirror, object store, or handoff process needs a different artifact name, copy the release ZIP under that exact name and let the verifier check that basename's tokens against the internal `VERSION` entry.

## Non-claims

This does not change the release ZIP member format, manifest format, schema semantics, or voting-process claims. It does not attempt to police every possible filesystem alias such as hard links. It only prevents symlink-based aliasing from hiding the filename presented to the release ZIP verifier.

## Compression posture

This revision adds one compact release-engineering document and two symlink-input probes. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/683-release-filename-version-token-coherence-firewall.md`
- `scripts/verify_release_zip.py`
- `scripts/check_release_zip_verifier.py`
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)
