# rev0106 page-proof sentinel and hash seal

This compatibility note preserves the rev0106 page-proof probe filename used by the datacube audit while documenting the final rev0106 shape.

rev0105 introduced the sentinel distinction: `choice_page_location_checked` records whether page proof was checked, while `choice_page_location_found` records whether the selected action was positively located. rev0106 keeps that `ActionTrace.v8` sentinel surface parseable and extends it to `ActionTrace.v9` with `choice_page_location_hash=`.

The v9 hash is `LegalActionPageLocation.v1`: a compact seal over page schema, choice kind, chooser, StateCore hash, ChoiceRequest hash, page cursors, page counts, page hash, and selected action hash. Replay and receipt validation reject missing or stale page-location hash evidence before mutation.

Audit probe anchors: legacy trace text used `choice_page_checked`; the rev0105 regression `test_action_trace_replay_rejects_applied_choice_page_proof_elision_without_mutation` remains in the suite; replay reports `ChoicePageLocationMismatch` for page-proof/context/count/hash drift before mutation.
