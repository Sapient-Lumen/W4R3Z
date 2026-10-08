# Scenario — Web hidden-input fullscreen breaks candidate anchor

This scenario models the current Web/WASM fallback lane where a hidden input is used to capture composition.
The point is to keep **backend-capability truth** honest:

- composition can be captured,
- but candidate-window anchoring may be approximate,
- and fullscreen behavior may require manual review rather than a fake native-support claim.
