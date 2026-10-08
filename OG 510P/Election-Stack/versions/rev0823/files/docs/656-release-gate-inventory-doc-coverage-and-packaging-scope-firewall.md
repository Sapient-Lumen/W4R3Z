# 656 — Release-gate inventory doc coverage and packaging-scope firewall

**Track:** Shared / Release engineering

This document records the v783 audit/reconstruction pass for two small release-engineering seams that survived the v781/v782 control-flow repairs. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

The runner in `scripts/release_gate.py` was enforcing more checks than the human control doc described. That is safer than the reverse, but it still creates a review hazard: maintainers can read `docs/162-release-and-ci-evidence-pipeline.md`, believe they have audited the release gate, and miss child checks that are actually part of the release verdict.

The concrete v783 diff was not a policy dispute; it was inventory drift. Several active child steps in the runner were absent from the release-gate control doc, including tombstone-index generation, public-artifact packet linting, publication/milestone registry checks, observer-kit JCS mirroring, platform-media companion tags, verifier-profile/surface-anomaly registries, and several voter-facing surface triplet/range/high-risk controls.

A second scope seam was packaging-specific. `MANIFEST.sha256`, cache hygiene, markdown scanning, size accounting, and deterministic ZIP construction each carried their own cache/build exclusion list. Those lists mostly overlapped, but they did not name exactly the same local-only paths. A small temporary directory or compiled-cache variant could therefore be outside the manifest while still being handled inconsistently by packaging or local scans.

A third locality seam appeared in example-packet verification. `scripts/check_example_packets.py` used to spawn the observer verifier once per packet. The whole release-gate step was bounded, but a packet-local verifier stall could still be reported as an undifferentiated step timeout rather than as a specific packet failure.

## Reconstruction rule

The release gate now carries an inventory-coverage check:

- `scripts/check_release_gate_doc_coverage.py` parses the authoritative child-step list in `scripts/release_gate.py`.
- It parses `docs/162-release-and-ci-evidence-pipeline.md` for `scripts/*.py` mentions.
- It fails if any release-gate child script is missing from the human control doc.
- `docs/162-release-and-ci-evidence-pipeline.md` has been backfilled with the current omitted child steps and now names every child script executed by the runner.

Example-packet verification was tightened for locality:

- `scripts/check_example_packets.py` now calls the same core verification functions used by `tools/observer_verify_packet.py` inside the checker process, so the gate reports the specific packet and problem list instead of depending on repeated verifier subprocesses.
- CLI smoke coverage remains in the operator-tool smoke lane; this check is now the offline packet-integrity lane.

Packaging scope was tightened without adding new artifacts:

- `scripts/check_no_cache_artifacts.py` now treats `tmp_emit_pvr/` as a forbidden build/cache directory, alongside interpreter and dependency caches.
- `scripts/build_release_zip.py` now excludes the same local-only cache families that the manifest and hygiene checks already treat as non-normative: Python bytecode variants, `.mypy_cache/`, `.ruff_cache/`, `.venv/`, `node_modules/`, and `tmp_emit_pvr/`.
- `scripts/_shared/md_scan.py` and `scripts/check_size_budget.py` now skip the same cache/build directory families for local scans and budget accounting.

## Maintainer rule

When a future patch adds, removes, or renames a release-gate child step, it must update `docs/162-release-and-ci-evidence-pipeline.md` in the same patch. The new coverage checker should fail before a reviewer has to notice the omission manually.

When a future patch creates a local-only output directory, it must classify that directory across all four release surfaces before the directory becomes normal:

1. manifest inclusion/exclusion;
2. deterministic ZIP inclusion/exclusion;
3. cache/build hygiene failure or allowance;
4. scan/budget treatment.

If any one of the four answers differs, the patch should say why. Otherwise, local-only bytes can become invisible to the manifest but visible to the release ZIP, or invisible to scans but still costly in packaged output.

## Compression posture

This revision adds one compact checker and one compact control document, and refactors an existing packet check for failure locality. It does not add external sources, downloaded bodies, new schemas, or a new public-answer surface. The useful invariant is a meta-control: release-check inventory and packaging-scope boundaries should be enforced by small scripts, not maintained as reviewer folklore.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/654-release-gate-subprocess-timeouts-and-ambient-environment-fail-closed-discipline.md`
- `docs/655-release-gate-failure-locality-failfast-and-manifest-write-quarantine.md`
- `scripts/release_gate.py`
- `scripts/check_release_gate_doc_coverage.py`
- `scripts/check_example_packets.py`
- `scripts/check_no_cache_artifacts.py`
- `scripts/build_release_zip.py`
- `scripts/build_manifest.py`
