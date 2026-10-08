# Axis-hygiene audit report — rev0314

Result: pass.

Rev0314 adds wealth/property/rent and public-procurement/industrial-policy axis gates.

## Wealth/property/rent

- Wealth `rent_extraction anti-pattern` records before: 2
- Wealth `rent_extraction anti-pattern` records after: 0
- Wealth `compliance_theater anti-pattern` records before: 2
- Wealth `compliance_theater anti-pattern` records after: 0
- Wealth `public_loss_private_upside anti-pattern` records before: 1
- Wealth `public_loss_private_upside anti-pattern` records after: 0
- Wealth `price_pass_through burden` records before: 3
- Wealth `price_pass_through burden` records after: 0
- Wealth `deferral remedy` records before: 6
- Wealth `deferral remedy` records after: 0

## Procurement / industrial policy

- Procurement `rent_extraction anti-pattern` records before: 5
- Procurement `rent_extraction anti-pattern` records after: 0
- Procurement `access_exclusion anti-pattern` records before: 2
- Procurement `access_exclusion anti-pattern` records after: 0
- Procurement `compliance_theater anti-pattern` records before: 1
- Procurement `compliance_theater anti-pattern` records after: 0
- Procurement `price_pass_through burden` records before: 5
- Procurement `price_pass_through burden` records after: 0
- Procurement `clawback remedy` records before: 5
- Procurement `clawback remedy` records after: 0

## Compressed-axis metrics after the refactor

- `declared_anti_pattern_values_after`: 214
- `declared_base_values_after`: 104
- `declared_instrument_values_after`: 37
- `declared_proof_posture_values_after`: 80
- `declared_review_trigger_values_after`: 163
- `route_anti_pattern_singletons_after`: 113
- `route_anti_pattern_singletons_before`: 228
- `route_anti_pattern_unique_after`: 164
- `route_anti_pattern_unique_before`: 310
- `route_anti_pattern_uses_after`: 440
- `route_axis_unique_values_after`: 1613
- `route_axis_value_uses_after`: 7106
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
