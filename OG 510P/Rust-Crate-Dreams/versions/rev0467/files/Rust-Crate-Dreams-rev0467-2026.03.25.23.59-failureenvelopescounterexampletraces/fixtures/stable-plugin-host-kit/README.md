
# Stable Plugin Host Kit fixtures

These fixtures exercise the `0.1` artifact vocabulary for **P-0081 Stable Plugin Host Kit**.

## Core schemas

- `abi-surface.receipt.schema.json`
- `capability-negotiation.receipt.schema.json`
- `lifecycle-posture.receipt.schema.json`
- `compatibility-witness.receipt.schema.json`
- `plugin-bundle.manifest.schema.json`

## Scenario families

- `abi_stable_prefix_module_adds_optional_field_without_breaking_loader/` — additive prefix evolution must stay distinct from hard ABI breaks.
- `libloading_unload_unknowns_require_restart_or_no_unload/` — native loading does not automatically imply safe unload or hot reload.
- `serialized_boundary_fallback_is_not_same_as_abi_stable_surface/` — useful fallback boundaries still need explicit downgraded surface classes.
- `optional_capability_negotiation_must_be_explicit_not_readme_folklore/` — optional APIs and downgrades need a machine-readable receipt.

The point of this fixture pack is to stop future passes from flattening:

- authoritative ABI surface,
- optional capability negotiation,
- load/unload/reload truth,
- and compatibility evidence

into one fake “we have native plugins” story.
