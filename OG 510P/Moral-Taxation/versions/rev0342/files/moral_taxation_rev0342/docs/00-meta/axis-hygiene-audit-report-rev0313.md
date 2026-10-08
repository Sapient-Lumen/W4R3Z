# Axis-hygiene audit report — rev0313

Result: pass.

Rev0313 adds a financial-system-risk guarantee/reserve/custody axis gate.

- Financial `rent_extraction` anti-pattern records before: 3
- Financial `rent_extraction` anti-pattern records after: 0
- Financial `public_loss_private_upside` anti-pattern records before: 3
- Financial `public_loss_private_upside` anti-pattern records after: 0
- Financial `compliance_theater` anti-pattern records before: 1
- Financial `compliance_theater` anti-pattern records after: 0
- Financial `platform_account` delivery records before: 1
- Financial `platform_account` delivery records after: 0
- Financial `legal_risk_transfer` burden records before: 1
- Financial `legal_risk_transfer` burden records after: 0
- Financial `fee_surcharge` burden records before: 1
- Financial `fee_surcharge` burden records after: 0
- Financial `clawback` remedy records before: 7
- Financial `clawback` remedy records after: 0
- Financial `disclosure` remedy records before: 1
- Financial `disclosure` remedy records after: 0

Compressed-axis metrics after the refactor:

- `declared_anti_pattern_values_after`: 214
- `declared_base_values_after`: 104
- `declared_instrument_values_after`: 37
- `declared_proof_posture_values_after`: 80
- `declared_review_trigger_values_after`: 163
- `route_anti_pattern_singletons_after`: 116
- `route_anti_pattern_singletons_before`: 228
- `route_anti_pattern_unique_after`: 164
- `route_anti_pattern_unique_before`: 310
- `route_anti_pattern_uses_after`: 449
- `route_axis_unique_values_after`: 1596
- `route_axis_value_uses_after`: 7117
- `route_base_singletons_after`: 0
- `route_base_unique_after`: 20
- `route_base_uses_after`: 285
- `route_instrument_singletons_after`: 0
- `route_instrument_unique_after`: 21
- `route_instrument_uses_after`: 404
- `route_proof_posture_singletons_after`: 0
- `route_proof_posture_unique_after`: 29
- `route_proof_posture_uses_after`: 301
- `route_review_trigger_singletons_after`: 98
- `route_review_trigger_singletons_before`: 206
- `route_review_trigger_unique_after`: 125
- `route_review_trigger_unique_before`: 270
- `route_review_trigger_uses_after`: 350
