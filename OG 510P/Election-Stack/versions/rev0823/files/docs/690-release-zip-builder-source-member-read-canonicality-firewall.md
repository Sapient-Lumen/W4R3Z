# 690 — Release ZIP builder source-member read canonicality firewall

**Track:** Shared / Release engineering

This document records a v815 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v809 through v814 progressively made the release artifact path boundary concrete: the ZIP verifier rejects ambiguous or symlink-routed input paths, the safe extractor preserves the verifier's accepted byte snapshot, the ZIP builder rejects ambiguous or symlink-routed output paths, and the ZIP builder rejects ambiguous or symlink-routed source roots.

The adjacent construction-side seam was individual source-member reading. `scripts/build_release_zip.py` discovered release members, but then later read each member with ordinary path opens. It also used `Path.resolve()` when deciding whether to skip the output ZIP path during member discovery. Those behaviors left two avoidable ambiguities:

```text
source member symlink -> output artifact       # hidden by resolved output-skip comparison
source member regular file -> symlink swap     # discovered as regular, then followed during read
```

The project already treats release-scope symlinks and special files as invalid source material. The builder therefore should not resolve source members before file-type checks, and it should recheck the final source member path immediately before reading bytes into the release ZIP.

## Reconstruction rule

Release ZIP construction now treats each source member read as a final regular-file boundary:

- skip the output ZIP only when the candidate source path lexically equals the audited output path;
- never use `Path.resolve()` to decide that a governed source member may be ignored as an output alias;
- recheck each selected source member with `lstat()` immediately before reading;
- reject source members that are symlinks at read time;
- reject source members that are not regular files at read time;
- open source members through a descriptor that uses `O_NOFOLLOW` where available;
- use `O_NONBLOCK` where available so a late special-file replacement cannot block the builder before type rejection;
- compare the opened descriptor identity with the pre-open `lstat()` identity;
- reject source members whose size changes while being read.

This mirrors the verifier's single-snapshot posture at the builder member boundary: the byte stream written to the ZIP must come from the regular file that was just audited, not from a path alias reached after a late replacement.

## Enforcement surfaces

v815 updates `scripts/build_release_zip.py` so `release_file_names()` no longer resolves source paths for the output-ZIP exclusion, and `_write_zip_bytes()` reads member bytes through a read-time regular-file/symlink firewall.

v815 extends `scripts/check_release_builder_filesystem_policy.py` with probes for:

- a governed symlink whose target is the requested output ZIP, which must be reported as a symlink rather than skipped as the output artifact;
- a selected source member swapped to a symlink after discovery and before ZIP writing, which must fail before any release ZIP is published.

## Operator effect

No normal release command changes. Canonical usage remains:

```text
python3 scripts/build_release_zip.py --out dist/The-Election-Stack-rev0815.zip
```

The stricter behavior only affects unsafe local trees or unstable local edits. A release-scope symlink, FIFO, device, or source file replaced while the builder is reading now fails closed instead of being followed, packaged, or silently ignored as an output alias.

## Non-claims

This does not make a mutable local checkout a secure build substrate, does not add filesystem locking, and does not claim race-free construction against a privileged local adversary. It closes a maintainer-error and aliasing seam by requiring each selected source member to still be the same regular file when its bytes are read.

This does not change release ZIP member names, manifest grammar, schema semantics, voter-facing surfaces, evidence packet semantics, or election-process claims.

## Compression posture

This revision adds one compact release-engineering document and builder-source-member regression probes. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/689-release-zip-builder-source-root-canonicality-firewall.md`
- `docs/688-release-zip-builder-output-path-canonicality-firewall.md`
- `docs/685-release-zip-single-snapshot-verification-firewall.md`
- `docs/672-release-builder-byte-exact-manifest-and-file-type-firewall.md`
- `scripts/build_release_zip.py`
- `scripts/check_release_builder_filesystem_policy.py`
- `scripts/verify_release_zip.py`
- `scripts/extract_release_zip.py`
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)
