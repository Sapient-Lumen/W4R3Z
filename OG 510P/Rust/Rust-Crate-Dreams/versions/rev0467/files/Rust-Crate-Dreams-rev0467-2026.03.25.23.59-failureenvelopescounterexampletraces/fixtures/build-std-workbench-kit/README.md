# Build-Std Workbench Kit fixtures

These fixtures are for **P-0430 Build-Std Workbench Kit**.

The point of this fixture pack is to freeze the support layer **above** Cargo's raw `build-std` substrate:

- one stage-aware sysroot recipe,
- one sysroot lock,
- one direct build receipt,
- one stage-posture report,
- one diff vocabulary,
- and scenario packs where the hard part is stage posture, source provenance, or target-modifier drift.

These fixtures should stay distinct from:

- ABI coherence profiles,
- sanitizer or BorrowSanitizer evidence bundles,
- source-path / debug-source hygiene contracts,
- and compile-time-deps/editor parity workflows.

Scenario families in this pass:
- `manual_core_alloc_custom_target/`
- `patched_std_overlay_drift/`
- `automatic_rebuild_policy_pending/`
- `target_modifier_profile_probe/`
