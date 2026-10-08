# 692 — Release manifest member-read canonicality firewall

**Track:** Shared / Release engineering

This document records a v817 release hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

v815 and v816 tightened release ZIP construction so selected source members are not packaged through symlinked leaves or symlink-routed parent directories. The adjacent manifest surface still hashed release-scope files through ordinary `Path.open()` calls after discovery.

That left the manifest builder and extracted-tree manifest verifier stricter at discovery time than at hash-read time. A local tree could be discovered as ordinary files and directories, then a leaf file or parent directory could be replaced by a symlink before the bytes were hashed. The resulting hash could describe bytes read through an alias route rather than the concrete release member route that was just inspected.

For example:

```text
repo/tmp_release_manifest_parent_probe/leaf.md     # discovered as an ordinary file
repo/tmp_release_manifest_parent_probe -> target/  # parent swapped before hashing
repo/tmp_release_manifest_parent_probe/leaf.md     # hash read is routed through the symlinked parent
```

That is not a normal maintainer workflow, but it is the same route-ambiguity class already closed for release ZIP inputs, safe extraction, and ZIP builder source reads. The manifest and ZIP builder must enforce the same boundary: bytes sealed into `MANIFEST.sha256` must be read through the concrete member route being audited.

## Reconstruction rule

Manifest hashing now treats the member route as part of the hash boundary:

- reopen the manifest root as a concrete directory route before hashing a member;
- walk every member parent component relative to an already-open directory descriptor;
- use no-follow directory opens where the runtime supports them;
- reject member ancestry components that cannot be opened as concrete directories without following symlinks;
- open the leaf member relative to the audited parent descriptor;
- require the leaf to be a regular file;
- reject final-path symlinks where the runtime exposes `O_NOFOLLOW`;
- reject member identity or size drift while bytes are being read.

The same helper is used for release manifest generation and for recipient-side extracted-tree manifest verification, so the source tree and extracted tree have aligned hash-read semantics.

## Enforcement surfaces

v817 updates `scripts/build_manifest.py` with no-follow member-read helpers and changes manifest generation to hash each governed release member through that route-aware reader.

v817 updates `scripts/verify_manifest.py` so extracted-tree hash checks use the same route-aware member reader instead of reopening `root / rel` as one pathname.

v817 extends `scripts/check_release_builder_filesystem_policy.py` with manifest leaf-symlink and parent-symlink swap probes. It also extends `scripts/check_manifest_verifier.py` with recipient-side hash-read symlink-swap probes.

## Operator effect

No normal release command changes. Canonical manifest refresh remains:

```text
python3 scripts/build_manifest.py
```

Canonical extracted-tree verification remains:

```text
python3 scripts/verify_manifest.py /path/to/extracted/release
```

The stricter behavior only affects unsafe or unstable local trees. If a release-scope member's leaf or parent route becomes symlinked between discovery and hashing, manifest generation or extracted-tree verification fails closed instead of sealing or accepting bytes read through the redirected route.

## Non-claims

This does not make a mutable checkout or extracted tree a secure build substrate, does not add filesystem locking, and does not claim race-free operation against a privileged local adversary. It narrows a concrete aliasing seam by requiring the member route used for hashing to be the route audited immediately before the file descriptor is opened.

This does not change release ZIP member names, manifest grammar, schema semantics, voter-facing surfaces, evidence packet semantics, or election-process claims.

## Compression posture

This revision adds one compact release-engineering document and route-aware manifest hash probes. It does not add external-source bodies, registries, voter-facing public-answer surfaces, or new election-process claims.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/691-release-zip-builder-source-member-ancestry-openat-firewall.md`
- `docs/690-release-zip-builder-source-member-read-canonicality-firewall.md`
- `docs/689-release-zip-builder-source-root-canonicality-firewall.md`
- `docs/688-release-zip-builder-output-path-canonicality-firewall.md`
- `docs/685-release-zip-single-snapshot-verification-firewall.md`
- `docs/672-release-builder-byte-exact-manifest-and-file-type-firewall.md`
- `scripts/build_manifest.py`
- `scripts/verify_manifest.py`
- `scripts/check_release_builder_filesystem_policy.py`
- `scripts/check_manifest_verifier.py`
- `scripts/build_release_zip.py`
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)
