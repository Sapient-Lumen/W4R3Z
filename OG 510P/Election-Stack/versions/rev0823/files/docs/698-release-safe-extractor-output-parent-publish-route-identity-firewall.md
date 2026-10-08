# 698 — Release safe-extractor output-parent publish route identity firewall

**Track:** Shared / Release engineering

This document records a v823 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v822 made the temporary extraction tree identity-bearing: the directory that is populated, manifest-verified, and published must remain the same directory. The adjacent publication seam was the output parent route. `scripts/extract_release_zip.py` rejected lexically ambiguous and symlink-routed output paths, but the parent directory used to hold the temporary extraction tree and receive the final rename was still addressed by pathname at several points.

That left a narrow local race: after the extractor created and preflighted the output parent, a local actor could replace that parent route before temporary-directory creation, output cleanup, or final publication. The temporary-root identity checks would catch many swaps, but the publication parent itself was not explicitly pinned as the same local directory object from setup through rename.

## Reconstruction rule

Safe extraction now treats the output parent directory as an identity-bearing release boundary:

- after output-parent creation and output-target preflight, the extractor records the parent directory identity;
- temporary extraction is allowed only while the output parent still names that same directory;
- member-copy, directory-mode canonicalization, extracted-tree manifest verification, output cleanup, and final publication recheck the parent identity;
- destructive cleanup for an existing output directory is routed through the pinned parent directory where descriptor-based routing is available;
- final publication uses a rename through the pinned parent directory descriptor where supported, rather than a fresh parent pathname;
- a parent that becomes a symlink, non-directory, missing path, or different directory fails closed before publication.

This connects the v812 verifier-snapshot bridge, v821 no-follow member writes, and v822 temporary-root identity rule to one concrete publication parent.

## Enforcement surfaces

v823 updates `scripts/extract_release_zip.py` with output-parent identity capture, repeated parent identity rechecks, descriptor-routed output cleanup where available, and descriptor-routed final rename where available.

v823 extends `scripts/check_release_safe_extractor.py` with an output-parent route swap probe. The probe verifies a temporary tree, swaps the output parent route before cleanup/publication, and requires extraction to fail without publishing into either the replacement parent or the original parent.

## Operator effect

Normal recipient use remains:

```text
python3 scripts/extract_release_zip.py dist/The-Election-Stack_<VERSION>.zip election-stack-<VERSION>
```

The difference is fail-closed behavior if the output parent directory route changes during extraction. In that case the tool reports an output-parent identity failure and does not publish the extracted release tree.

## Non-claims

This does not add OS-level sandboxing, mandatory access control, repository locking, or protection against a privileged local actor. It closes the narrower extractor publication seam: the parent directory used for temporary extraction, cleanup, and final publication must be the same concrete directory the extractor preflighted.

This does not change election-process claims, evidence packet semantics, schema semantics, public-answer surfaces, release ZIP member names, manifest grammar, ZIP byte canonicality, or output-directory clean/replace consent rules.

## Compression posture

This revision adds one compact release-engineering document and one bounded smoke probe. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/697-release-safe-extractor-temp-root-publish-identity-firewall.md`
- `docs/696-release-safe-extractor-member-write-openat-firewall.md`
- `docs/687-release-safe-extractor-zip-input-snapshot-bridge-firewall.md`
- `docs/681-release-safe-extractor-lexical-output-path-canonicality-firewall.md`
- `docs/674-release-safe-extractor-output-ancestry-firewall.md`
- `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`
- `scripts/extract_release_zip.py`
- `scripts/check_release_safe_extractor.py`
- `scripts/verify_release_zip.py`
- `scripts/verify_manifest.py`
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)
