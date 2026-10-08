# 697 — Release safe-extractor temporary-root publish identity firewall

**Track:** Shared / Release engineering

This document records a v822 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v821 made member writes stricter: accepted ZIP members are created through no-follow extraction-directory routes where available, so a swapped member parent cannot receive verified bytes. The adjacent publication seam was the temporary extraction tree itself. After extraction and post-extraction manifest verification, `scripts/extract_release_zip.py` still published the temporary tree by path. If a local actor replaced that already-verified temporary directory with a symlink or different directory between verification and final rename, the extractor could publish a path that was no longer the tree it had verified.

The extractor already rejected symlinked output ancestry and verified the extracted tree before publication. v822 adds a narrower identity rule: the temporary extraction root that is created, populated, verified, and renamed must remain the same local directory object throughout the pipeline.

## Reconstruction rule

Safe extraction now treats the temporary extraction root as an identity-bearing release boundary:

- immediately after creating the temporary extraction directory, the extractor records its local directory identity;
- member writes check that the temporary root still names that same directory before opening release member destinations;
- the temporary root identity is rechecked after member copy, after directory-mode canonicalization, after extracted-tree manifest verification, after output cleanup/preparation, and immediately before the final rename;
- a temporary root that becomes a symlink, non-directory, missing path, or different directory fails closed before publication;
- after the final rename, the published output root is checked against the same captured identity.

This keeps the v812 verifier-snapshot bridge, v821 no-follow member writes, and the older output-target ancestry/lexical firewalls connected to a single concrete temporary tree.

## Enforcement surfaces

v822 updates `scripts/extract_release_zip.py` with temporary-root identity capture and repeated identity rechecks around the extraction and publication stages. The change does not alter release ZIP bytes, ZIP member grammar, manifest grammar, or operator-facing output consent semantics.

v822 extends `scripts/check_release_safe_extractor.py` with a post-verification temporary-root swap probe. The probe verifies a temporary tree, replaces that path with a symlink before publication, and requires the extractor to fail without publishing the swapped path.

## Operator effect

Normal recipient use remains:

```text
python3 scripts/extract_release_zip.py dist/The-Election-Stack_<VERSION>.zip election-stack-<VERSION>
```

The difference is fail-closed behavior if the verified temporary extraction directory is replaced after verification but before publication. In that case the tool reports the temporary-root identity failure, removes the temporary path where safe, and does not publish an output directory.

## Non-claims

This does not add OS-level sandboxing, repository locking, mandatory access control, or a complete defense against a privileged local actor. It closes the narrower extractor publication seam: the directory that becomes the published release tree must be the same directory the extractor created and verified.

This does not change election-process claims, evidence packet semantics, schema semantics, public-answer surfaces, release member names, manifest grammar, ZIP byte canonicality, or output-directory clean/replace consent rules.

## Compression posture

This revision adds one compact release-engineering document and one bounded smoke probe. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
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
