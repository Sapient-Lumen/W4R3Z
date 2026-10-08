# 691 — Release ZIP builder source-member ancestry openat firewall

**Track:** Shared / Release engineering

This document records a v816 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v815 made release ZIP source-member reads stricter at the leaf-file boundary: selected members are rechecked immediately before packaging, final-path symlinks are rejected, and member bytes are read through a regular-file descriptor with size/identity drift checks.

The adjacent construction-side seam was the parent-directory route to each selected source member. A source member could be discovered under an ordinary directory, then that parent directory could be replaced by a symlink before the read-time leaf-file check. A final-file `O_NOFOLLOW` check does not by itself prove that the parent route is still concrete.

For example:

```text
repo/tmp_release_source_parent_probe/leaf.md     # discovered as an ordinary file
repo/tmp_release_source_parent_probe -> target/  # parent swapped before read
repo/tmp_release_source_parent_probe/leaf.md     # leaf opens as ordinary file through redirected ancestry
```

That is not a normal maintainer workflow, but it is the same class of local route ambiguity that v809 through v815 have been closing: the release builder, verifier, and safe extractor should not silently follow filesystem aliases while constructing or consuming official archive bytes.

## Reconstruction rule

Release ZIP construction now treats the source-member ancestry as part of the read-time boundary:

- reopen the accepted source root as a concrete directory route before member reads;
- walk every source-member parent component relative to an already-open directory descriptor;
- use no-follow directory opens where the runtime supports them;
- reject any source-member ancestry component that cannot be opened as a concrete directory without following symlinks;
- then open the leaf member relative to the audited parent descriptor;
- keep the v815 regular-file, no-final-symlink, identity, and size-drift checks for the leaf file.

On POSIX runtimes with `openat`-style directory descriptors, this avoids converting a discovered release path into a later symlink-routed path read. On runtimes without that support, the builder keeps the existing fail-closed path and type checks.

## Enforcement surfaces

v816 updates `scripts/build_release_zip.py` so `_read_source_member_bytes()` no longer opens `repo_root / rel` as one pathname. It opens the source root and each parent directory component first, then opens the final file relative to that audited parent descriptor.

v816 extends `scripts/check_release_builder_filesystem_policy.py` with a post-discovery parent-directory symlink-swap probe. The probe discovers a governed source file, replaces its parent directory with a symlink to a different directory before ZIP writing, and requires the builder to reject the ancestry before publishing any archive.

## Operator effect

No normal release command changes. Canonical usage remains:

```text
python3 scripts/build_release_zip.py --out dist/The-Election-Stack-rev0816.zip
```

The stricter behavior only affects unsafe or unstable local trees. If a release-scope source member's parent route becomes a symlink between discovery and packaging, the build fails closed instead of packaging bytes through the redirected route.

## Non-claims

This does not make a mutable local checkout a secure build substrate, does not add filesystem locking, and does not claim race-free construction against a privileged local adversary. It narrows a concrete aliasing seam by requiring the member ancestry used for packaging to be the ancestry audited immediately before the file descriptor is opened.

This does not change release ZIP member names, manifest grammar, schema semantics, voter-facing surfaces, evidence packet semantics, or election-process claims.

## Compression posture

This revision adds one compact release-engineering document and one builder-source-member ancestry regression probe. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/690-release-zip-builder-source-member-read-canonicality-firewall.md`
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
