# Cargo Resolve Why Kit fixtures

This fixture family exists to make **P-0468 Cargo Resolver Explanation Kit** more concrete.

The goal is to emit compact review artifacts for recurring questions like:

- why is this feature active,
- why was this version chosen,
- why was the same package built multiple times,
- what changed between two resolution snapshots,
- how much of this explanation is exact versus approximate,
- whether workspace selection or mixed-MSRV policy materially changed the answer,
- what the subject explicitly asked Cargo to keep on or off,
- and where an effective dependency policy actually came from when `[workspace.dependencies]`, member manifests, and target-specific inherited edges all participate,
- and whether a feature-like name was explicit, implicit, hidden by `dep:`, or only conditionally meaningful because weak forwarding requires prior activation,
- and which dependency key, package name, rename field, and registry/index surface actually referred to the dependency under discussion.

## Intended first scenarios

1. `workspace_feature_forwarding`
2. `package_mode_feature_split`
3. `lockfile_precise_update`
4. `msrv_workspace_version_choice`
5. `workspace_selection_masks_missing_feature`
6. `manual_review_required`
7. `resolver2_dev_normal_tree_merge_warning`
8. `nonmatching_target_specific_dependency_omitted`
9. `proc_macro_build_normal_lane_manual_review`
10. `workspace_mode_out_of_selection_feature_pressure`
11. `default_features_false_masked_by_workspace`
12. `bin_subject_feature_pressure`
13. `workspace_inherited_default_features_reenabled`
14. `target_specific_inherited_dependency_scope`
15. `dep_syntax_hidden_optional_alias`
16. `weak_dependency_feature_requires_prior_activation`
17. `renamed_optional_dependency_feature_namespace`
18. `workspace_inherited_dependency_rename_ignored`

## Minimal bundle for 0.1

- `resolve-why.lock`
- `feature-causes.json`
- `version-choices.json`
- `duplicate-builds.json`
- `lane-partition.report.json`
- `platform-coverage.report.json`
- `unification-scope.report.json`
- `feature-intent.report.json`
- `dependency-origin.report.json`
- `feature-origin.report.json`
- `dependency-identity.report.json`
- `resolver-choice.receipt.json`
- `notes.md`

Later overlays may add:
- `resolution-diff.report.json`
- richer `--unit-graph` imports
- third-party graph-simulation provenance details

## Design rule

This fixture family should optimize for **short cause chains**, **compact influence lists**, and **frozen selection scope** that are obviously reviewable.

If Cargo does not directly expose a fact, the bundle must mark that explanation as conservative inference rather than pretending it is solver ground truth.
If a view is only “close to the build” rather than exact, the receipt should say so.

## Current planning stance

This family is **not** trying to replace `guppy`, `hakari`, `cargo tree`, or Cargo plumbing work.
It is trying to standardize the receiver-facing artifact those surfaces still do not hand people by default.
