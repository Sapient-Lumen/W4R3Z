# Node-API Package & Prebuild Contract Kit fixtures

This fixture family now treats three review objects as first-class:

1. **prebuild coverage** — what native tuples actually shipped
2. **loader route** — how the package chooses native, default, local-build, or WASM paths
3. **publish identity** — what npm trusted-publishing/provenance posture the release really has

Scenario families:
- `musl_gap_hidden_by_local_build_fallback/` — native tuple gap masked by a source-build escape hatch
- `node_addons_native_path_with_default_wasm_fallback/` — explicit `node-addons` native route plus universal fallback path
- `trusted_publisher_provenance_present_but_manual_runtime_claims_still_need_review/` — strong publish identity that still does not settle support claims
