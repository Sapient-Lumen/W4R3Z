# Axis-hygiene audit report — rev0311

Result: pass.

Rev0311 adds a labor/care status-and-benefit axis gate.

- Labor/care `rent_extraction` anti-pattern records before: 6
- Labor/care `rent_extraction` anti-pattern records after: 0
- Labor/care `legal_risk_transfer` burden records before: 3
- Labor/care `legal_risk_transfer` burden records after: 0
- Labor/care public-channel-only delivery records before: 1
- Labor/care public-channel-only delivery records after: 0

Compressed-axis metrics after the refactor:

- `declared_anti_pattern_values_after`: 210
- `declared_base_values_after`: 104
- `declared_instrument_values_after`: 37
- `declared_proof_posture_values_after`: 80
- `declared_review_trigger_values_after`: 148
- `route_anti_pattern_singletons_after`: 116
- `route_anti_pattern_singletons_before`: 228
- `route_anti_pattern_unique_after`: 160
- `route_anti_pattern_unique_before`: 310
- `route_anti_pattern_uses_after`: 435
- `route_axis_unique_values_after`: 1435
- `route_axis_value_uses_after`: 7009
- `route_base_singletons_after`: 0
- `route_base_unique_after`: 20
- `route_base_uses_after`: 285
- `route_instrument_singletons_after`: 0
- `route_instrument_unique_after`: 21
- `route_instrument_uses_after`: 404
- `route_proof_posture_singletons_after`: 0
- `route_proof_posture_unique_after`: 29
- `route_proof_posture_uses_after`: 301
- `route_review_trigger_singletons_after`: 84
- `route_review_trigger_singletons_before`: 206
- `route_review_trigger_unique_after`: 111
- `route_review_trigger_unique_before`: 270
- `route_review_trigger_uses_after`: 341
