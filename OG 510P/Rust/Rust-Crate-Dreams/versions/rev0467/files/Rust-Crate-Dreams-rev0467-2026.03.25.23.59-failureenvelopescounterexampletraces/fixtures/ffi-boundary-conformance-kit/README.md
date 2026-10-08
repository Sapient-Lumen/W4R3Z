# ffi-boundary-conformance-kit fixtures

This fixture pack freezes a stronger artifact vocabulary for **P-0121 FFI Boundary & Bindings Conformance Kit**.

Artifacts:
- `interface-authority.import.schema.json`
- `projection-basis.receipt.schema.json`
- `derivative-parity.report.schema.json`
- `ownership-transfer.receipt.schema.json`
- `unwind-posture.receipt.schema.json`
- `callback-authority.receipt.schema.json`
- `callback-execution.report.schema.json`
- `callback-lifecycle.receipt.schema.json`
- `callback-completion.report.schema.json`
- `binding-coverage.report.schema.json`
- `layout-authority.receipt.schema.json`
- `error-channel.receipt.schema.json`
- `projection-drift.report.schema.json`
- `ffi-support-bundle.manifest.schema.json`

Scenario families:
- `borrowed_slice_must_not_share_ownership_receipt_with_foreign_free_buffer/`
- `extern_c_callback_wrapper_and_c_unwind_export_must_not_share_same_unwind_posture/`
- `mixed_binding_stack_must_not_claim_uniform_callback_or_coverage_strength/`
- `cxx_shared_type_and_opaque_type_need_separate_layout_authority_receipts/`
- `uniffi_flat_error_cxx_exception_and_wit_result_need_separate_error_channel_receipts/`
- `generated_header_is_derived_not_primary_interface_authority/`
- `cbindgen_configured_header_projection_needs_projection_basis_and_parity/`
- `diplomat_backend_attrs_make_projection_backend_specific/`
- `wit_bindgen_export_macro_and_custom_section_options_need_projection_basis/`
- `release_to_release_projection_change_needs_receiver_visible_drift_review/`
- `foreign_callback_requires_explicit_unregister_or_drop_story/`
- `uniffi_foreign_future_requires_exactly_once_completion_story/`
- `diplomat_callback_param_is_not_bidirectional_trait_surface/`
- `cxx_async_oneshot_adapter_is_not_native_async_surface/`
- `uniffi_foreign_trait_unexpected_error_mapping_must_not_stay_implicit/`
- `portable_bundle_keeps_callback_authority_completion_and_lifecycle_separate/`
- `portable_bundle_keeps_authority_projection_lifecycle_and_contract_separate/`
