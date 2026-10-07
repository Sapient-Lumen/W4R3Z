# Worked example support artifacts

This folder carries support material for `paper17_worked_example_receipt_interlock/paper.tex`.
The current cut is a freeze-oriented maintenance pass: the paper and support artifacts are being kept stable, and the folder now includes a deterministic materializer, a small compare helper, a lightweight validator, and a machine-readable artifact inventory so the worked example can be regenerated, navigated, and checked without turning the support objects into a second schema. The support manifest is now a self-describing, release-bound digest list, and together with the inventory it covers the JSON adjuncts, the worked-note source, and the tiny local helper scripts used to rebuild the bundle. The manifest and inventory also point back to each other by id and carry the current note version, so the compare report and validation report can identify one maintained bundle cut rather than two loosely paired maintenance files. The generated compare report and validation report also record the current release id, support-manifest id, and artifact-inventory id so a handoff reviewer can see which maintained bundle cut they summarize. On a clean rebuild, the compare emitter first binds the compare-report digest into `support_manifest.json`, and the validator then checks the persisted compare-report and validation-report bindings already on disk before appending the refreshed validation-report digest and rerunning once more to confirm the persisted bundle cut. Local render outputs such as `paper.pdf`, `paper.aux`, `paper.log`, `paper.out`, `pngcheck/` images, and `tools/__pycache__/` bytecode caches are transient build byproducts and are intentionally excluded from the maintained support bundle and from the packaged archive handoff.

Grouped by role:
- Core published claim objects: `example_receipt.json`, `example_abom.json`, `example_exposure_nf_registry.json`, `example_tw_decl.json`, `example_state_decl_registry.json`, `example_release_receipt.json`, `example_uvi.json`
- Guard / comparison adjuncts: `example_primary_surface_manifest.json`, `example_state_decl.json`, `example_change_control.json`, `example_compare_profile.json`, `example_compare_walkthrough.json`, `example_drift_cases.json`, `example_user_watch_policy.json`
- Replay / evidence adjuncts: `example_replay_plans.json` (with `plan_spec_id`), `example_support_bundle_map.json`, `example_verifier_report.json`
- Maintenance outputs: `example_artifact_inventory.json`, `example_compare_report.json`, `support_manifest.json`, `example_validation_report.json`, `README.md`, `paper.tex`, `tools/materialize_example.py`, `tools/emit_compare_report.py`, `tools/validate_example.py`, `tools/rebuild_example.sh`

Contents:
- `artifacts/example_receipt.json` - illustrative receipt payload with line items
- `artifacts/example_abom.json` - illustrative ABOM/OINL-style claim manifest
- `artifacts/example_exposure_nf_registry.json` - label-to-ENF-ID binding registry for the worked example
- `artifacts/example_tw_decl.json` - threat/window declaration object binding the TW label to `tw_id`
- `artifacts/example_state_decl_registry.json` - label-to-`state_decl_id` binding registry for the worked example (human `state_contract_id` → digest-bound `state_decl_id`)
- `artifacts/example_uvi.json` - illustrative user-verifiability record
- `artifacts/example_state_decl.json` - illustrative state declaration adjunct consumed by replay plans; includes digest-bound `state_decl_id`
- `artifacts/example_primary_surface_manifest.json` - illustrative primary-path assumption/invalidation manifest
- `artifacts/example_user_watch_policy.json` - illustrative client watch-policy adjunct for UVI drift
- `artifacts/example_change_control.json` - illustrative change-control / recertification adjunct for release drift
- `artifacts/example_replay_plans.json` - replay-plan catalog resolving `plan_id` values to workflow owners / required inputs, and binding each plan's semantics via `plan_spec_id`
- `artifacts/example_support_bundle_map.json` - operational map from `artifact_bundle` ids to concrete archive artifacts / support pointers
- `artifacts/example_compare_profile.json` - compact cross-release diff profile for OINL-style comparison
- `artifacts/example_compare_walkthrough.json` - one concrete prior-vs-current comparison keyed to the compare profile
- `artifacts/example_release_receipt.json` - illustrative release-binding object
- `artifacts/example_drift_cases.json` - tiny successor-release sketches for refresh-only / replay / recertification cases
- `artifacts/example_verifier_report.json` - compact replay summary for the worked example
- `artifacts/example_artifact_inventory.json` - machine-readable role inventory for the worked-example support bundle, including a back-pointer to the companion support manifest for the same maintained bundle cut
- `artifacts/example_compare_report.json` - machine-readable cross-release diff summary generated from the compare profile and compare walk-through
- `artifacts/example_validation_report.json` - validator output checking digest/reference and arithmetic consistency across the worked-example support objects
- `artifacts/support_manifest.json` - digest list for the support artifacts in this folder together with `paper.tex` and the tiny helper files named in the inventory, including a back-pointer to the companion artifact inventory
- `tools/materialize_example.py` - script that regenerates the JSON artifacts deterministically
- `tools/emit_compare_report.py` - script that emits the machine-readable compare report from the compare profile and compare walk-through
- `tools/validate_example.py` - script that checks digest/reference consistency and recomputes the worked arithmetic
- `tools/rebuild_example.sh` - one-shot helper that regenerates artifacts, emits the compare report, reruns validation, and rebuilds the paper

These are archive-internal working artifacts.
The paper itself remains source-only and treats them as supporting material available on request.

Suggested maintenance flow:

```bash
./tools/rebuild_example.sh
```

Equivalent step-by-step flow:

```bash
python tools/materialize_example.py
python tools/emit_compare_report.py
python tools/validate_example.py
```

The validator checks the current artifact inventory as well as the published digests and worked arithmetic, including coverage of `paper.tex` in the maintained support bundle and cross-reference agreement between the support manifest and artifact inventory. It also checks that the draft label and note version used by the release-bound JSON stay aligned with the current worked-note cut, that the compare walk-through / drift-case successor labels stay aligned with the current base release, and that the compare walk-through successor receipt digest is derived from the synthetic Case-B successor receipt rather than left as a placeholder. That prevents a newer paper revision from shipping stale release ids or a fake successor digest in the support bundle.


Transient local build outputs are convenient for spot-checking a revision, but they are not inventory-listed or digest-bound. The maintained bundle tracks the source-side support objects needed to regenerate and validate the worked example, not every local render or interpreter byproduct.


### Optional coarsening variant (large-alphabet audit made feasible)
- artifacts/example_coarsening_map_contact.json
- artifacts/example_profiling_evidence_contact_coarsened.json
- artifacts/example_receipt_contact_coarsened_variant.json
