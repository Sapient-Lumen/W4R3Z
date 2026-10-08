# 658 — Release packaging scope alignment, leading-dot normalization, and verifier CLI harness

**Track:** Shared / Release engineering

This document records the v786 reconstruction pass for release-package scope control. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

The v785 release repaired a concrete symptom: top-level local `*.log` transcripts no longer enter `MANIFEST.sha256`, the deterministic ZIP, or cache-artifact hygiene checks. That repair made the three surfaces agree for the observed case, but it still depended on parallel exclude logic staying aligned by convention.

The deeper invariant is stricter: apart from `MANIFEST.sha256` itself, every file selected by the deterministic ZIP builder must be sealed by `MANIFEST.sha256`, and every manifest-sealed file must be selected by the ZIP builder. Otherwise a release could ship an unsealed local artifact, or seal a file that the distributed archive omits.

While auditing that invariant, v786 also found a path-normalization seam in the ZIP builder: stripping the characters `.` and `/` with `lstrip("./")` can change a leading-dot path such as `.git/config` into `git/config` before exclusion predicates see it. The shipped archive does not contain `.git/`, but the release builder should reject that class of path by construction, not by accident.

## Reconstruction rule

`scripts/check_release_packaging_alignment.py` is now a release-gate child step. It compares the manifest builder's actual selected file set to the deterministic ZIP builder's actual selected file set and requires:

1. `zip_files == manifest_files + {"MANIFEST.sha256"}`;
2. known local-only paths such as `.git/`, `dist/`, `evidence/cache/`, `tmp_emit_pvr/`, top-level `*.log`, bytecode caches, and `node_modules/` are rejected by both predicates;
3. ordinary governed archive paths are accepted by both predicates.

This makes packaging-scope drift a gate failure instead of a manual review burden.

## Leading-dot normalization rule

Release path normalization may remove a literal leading `./` prefix, but it must not strip leading dots from path components. In particular, `.git/config` must remain `.git/config` until the exclusion rule sees it. v786 replaces character-set stripping with explicit `./` prefix removal in both the manifest predicate and the deterministic ZIP builder's normalizer.

## Shared CLI harness rule

Some release-gate drift tests need to invoke repository-local Python CLIs and assert on their stdout/stderr. Those checks should not spawn extra interpreters merely to exercise a local CLI, but they also should not mutate the parent process permanently.

`scripts/_cli_harness.py` provides a small stdlib-only in-process CLI runner that isolates `sys.argv`, stdout, stderr, cwd, `sys.path`, and bytecode-writing state around one `runpy` invocation. v786 wires the PacketVerificationReport linkage and emit-packet drift tests through this harness while preserving their observable command-line contract.

The top-level release gate still runs child checks in subprocesses. The harness is only for bounded, repository-local CLI calls inside an already-isolated child step.

## Release-gate placement

The v786 packaging-alignment check originally ran immediately after cache-artifact hygiene. As of v790, symlink and shared release-path-policy checks run first, then packaging alignment, ZIP verifier smoke probes, and extraction/rebuild invariance. That placement keeps non-portable filesystem entries and ambiguous member names out of temporary packaging probes before those probes compare manifest and ZIP scope.

## Compression posture

This revision adds one compact maintainer-control document and one release-gate drift firewall. It does not add external sources, downloaded bodies, schemas, registries, or a new public-answer surface.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/656-release-gate-inventory-doc-coverage-and-packaging-scope-firewall.md`
- `docs/657-release-gate-resumability-profiled-diagnostics-and-process-group-timeouts.md`
- `scripts/build_manifest.py`
- `scripts/build_release_zip.py`
- `scripts/check_release_packaging_alignment.py`
- `scripts/_cli_harness.py`
- `scripts/check_packet_verification_report_linkage.py`
- `scripts/check_packet_verification_report_emit_packet.py`
