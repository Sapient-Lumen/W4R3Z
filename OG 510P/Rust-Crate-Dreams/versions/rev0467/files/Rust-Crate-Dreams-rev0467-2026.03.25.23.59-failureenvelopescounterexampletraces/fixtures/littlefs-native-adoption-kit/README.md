# littlefs-native-adoption-kit fixtures

This fixture pack exists to make **P-0527 LittleFS Native Adoption Kit** concrete.

The goal is not to prove every flash or every power-failure model.
The goal is to make three truths reviewable:

1. **storage-adapter truth** — what backend assumptions are actually in play,
2. **compatibility truth** — what images/operations were really exercised,
3. **power-cut truth** — what interruption model was really tested.

## Core artifacts

- `storage-adapter.receipt.schema.json`
- `compatibility-witness.receipt.schema.json`
- `powercut-run.report.schema.json`

## Scenario families

- `upstream_image_roundtrip_witness/`
- `async_flash_cooperative_yield_receipt/`
- `interrupted_rewrite_recovers_last_known_good_state/`
