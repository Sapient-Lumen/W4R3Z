# Cargo Resolver Explanation Kit fixtures

These fixtures are for **P-0468 Cargo Resolver Explanation Kit**.

The point is to freeze the support layer above Cargo's resolver substrate:

- one capture lock,
- a reusable family of explanation/report schemas,
- one exactness/evidence-source receipt,
- and scenario packs for confusing resolver-pressure cases.

These fixtures should stay distinct from:

- Cargo's resolver implementation itself,
- PubGrub integration work,
- workspace-boundary discovery,
- build-analysis history storage,
- and broad MSRV planning / support policy crates.

Scenario families in this pass:
- `mixed_msrv_workspace_compromise/`
- `single_member_question_blurred_by_workspace_mode/`
- `inherited_renamed_target_specific_dependency_policy/`
