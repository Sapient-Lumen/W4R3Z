# Release Flow

This is the repository's release flow for public papers.

## Principle

The main drafting line stays alive.
Publication happens through a separate, slower release path.

## Label and link discipline

- Old already-published papers may continue using their existing **Mathematics** wiki links.
- New releases must use **Anonymity** in the published name.
- A future operator must never infer that the old label carries forward to new releases.

## States

1. **Drafting**
   - the paper is still being actively rewritten, split, merged, or re-scoped.
   - no release action is taken.

2. **Hold**
   - the paper is promising, but not yet stable enough for public freezing.
   - a hold note should explain what is still moving.

3. **Candidate**
   - the paper appears potentially publishable, but still requires explicit review against the conservative release criteria.
   - entry into Candidate is not permission to publish.

4. **Published-ready queue**
   - the paper has passed the conservative gate and is waiting for a gentle release slot.
   - the paper should remain unchanged except for final naming and packaging checks.

5. **Published**
   - the paper is copied into `published/` under the exact wiki-facing naming scheme.
   - the canonical artifact is the `.tex` file.

## Required movement rule

Movement is intentionally slow:

- Drafting -> Hold or Candidate
- Candidate -> Hold or Published-ready queue
- Published-ready queue -> Published

A paper should not jump directly from Drafting to Published.

## Repository expectations

- Every state change must be written down.
- Every publish decision must cite the source `.tex` path that was frozen.
- Every hold decision should name the blocking reason.
- The queue should stay small.
- The default outcome of a review is **no promotion**.

## Freeze-lane preflight

The release lane is separate from the maintenance lane. Resolver, support-bundle, schema, and transfer repairs may continue in the maintenance lane, but a release candidate should be frozen against a single source hash. First run `publishing/check_release_readiness.py` to check the queue as a set, then use `publishing/release_preflight.py` on exactly one selected source before copying anything into `published/`.

A release candidate must pass these source-preflight checks unless a written decision note records a narrow exception:

- the source `.tex` exists outside `published/`;
- the source is represented in the Published-ready queue by exact `QUEUE_INDEX.json` `source_tex` binding;
- the prospective published directory does not already exist;
- local citation and reference closure are clean;
- unallowlisted TODO/FIXME/TBD/XXX markers are absent;
- a clean temporary LaTeX build passes when `--compile` is used;
- the current source SHA-256 is recorded in the Candidate / Published-ready queue note and matches the source bytes being preflighted;
- the source SHA-256 is recorded again in the final publish decision or freeze receipt.

For artifact-governance papers, publish a minimal evidence pack with the frozen source rather than a naked `.tex`: `support_manifest.json`, `example_artifact_inventory.json`, `example_validation_report.json`, resolver/support-bundle maps when cited, and the validator or manifest excerpt needed to reproduce the pass.

The queue-level readiness audit is not a publication decision. It should show `publication_authorized=false`; publication still requires an explicit written decision note and a post-freeze surface rebuild.

Maintenance helper: after an intentional edit to a Candidate or Published-ready source, run `python3 -B publishing/refresh_queue_source_hashes.py --root .` and record why the queued source remains in that state. Then rerun `make verify-surfaces`.


## rev0808 dry-run freeze plan

Before copying a Published-ready paper into `published/`, inspect `reports/review_inventory_coverage.json`, `reports/evidence_pack_audit.json`, and `release_queue/NEXT_RELEASE_FREEZE_PLAN.md`. The freeze plan may name one static-pass source and prospective target path, but it is deliberately non-authorizing: `publication_authorized=false` must remain true until a separate written publication decision resolves evidence-pack, compile, metadata, provenance, and final-manifest gates.

The direct preflight now warns when artifact-governance language is present. Use `--evidence-mode require --evidence-pack path/to/manifest.json` when the evidence pack is present, or `--evidence-mode waive --evidence-waiver-id ID` only when a decision note records the waiver scope.


## rev0810 publication execution guard

The freeze lane now has a staged, non-public packet between preflight and publication. After evidence and clean-compile gates pass, `publishing/build_release_freeze_packet.py` materializes a copy of the selected source under `release_queue/freeze_packets/` and binds it to the evidence manifest, compile witness, freeze plan, queue note, and source SHA-256. This still does not authorize publication.

Before a new Anonymity entry is created under `published/`, run:

- `python3 -B publishing/check_freeze_packet_integrity.py --root .`
- `python3 -B publishing/check_publication_boundary.py --root .`

A future publish decision must name the freeze-packet manifest in addition to the source hash, target path, evidence manifest, and compile witness. The guarded publication helper refuses to copy into `published/` without those bindings.

## rev0811/rev0812 current-witness and publication-decision gate

Before a public copy is made, rebuild the selected clean-compile witness for the current revision:

```bash
python3 -B publishing/check_freeze_toolchain.py --root .
python3 -B publishing/build_freeze_compile_witness.py --root .
python3 -B publishing/check_freeze_compile_witness.py --root .
python3 -B publishing/build_publication_rehearsal.py --root .
```

`reports/freeze_compile_witness.json` must show `compile_gate_status=pass` before publication. If it shows `pending_current_toolchain_refresh`, the source-bound prior compile evidence is still useful, but the current publication compile gate remains open.

Then copy `release_queue/PUBLICATION_DECISION_TEMPLATE.md` into a dated decision note and complete it. The guarded helper will reject a decision note that does not name the source hash, evidence-pack manifest, compile witness, freeze-packet manifest, and exact target. A completed template is still not enough by itself; after the helper runs, public-surface classification, citation heads, provenance, schemas, reports, and manifests must be rebuilt.

After rebuilding surfaces, package with:

```bash
make package
```


### rev0814 — rebuild fixed-point guard

The archive now includes `publishing/check_rebuild_fixed_point_coverage.py` and `reports/rebuild_fixed_point_coverage.json` so tail-mutated rebuild surfaces cannot escape the declared convergence target set. No publication was authorized.

## Explicit publish-decision gate

The publication helper may only run against a completed decision note that contains `Publication action: publish` and all required source/evidence/compile/freeze/receipt bindings. The scanner in `publishing/check_publication_decision_authorization.py` turns incomplete or placeholder publish notes into publication blockers.


## rev0824 release-lane guard additions

Before any publication attempt, `reports/manifest_canonicality.json`, `reports/freeze_warning_resolution.json`, and `reports/toolchain_fingerprint.json` must pass. These checks prove that package manifests are canonical, freeze preflight warnings have explicit downstream resolution, and clean-compile evidence is bound to a TeX command fingerprint. They are blockers only and do not authorize publication.


## rev0825 release-lane guard addition

The release lane now includes Unicode/control-character hygiene. A candidate cannot advance to publication if any shipped text surface contains hidden C0/C1 controls beyond LF/TAB, bidi controls, invisible format controls, Unicode noncharacters, or surrogate code points.
