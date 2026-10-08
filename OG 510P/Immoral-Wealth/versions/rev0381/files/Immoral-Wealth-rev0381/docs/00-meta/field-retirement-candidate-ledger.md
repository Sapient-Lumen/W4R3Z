---
project: Immoral Wealth
status: schema_retirement_cutover_receipt
revision_current: rev0368
generated_at: 2026-06-18T14:06:00Z
---

# Field retirement candidate ledger — rev0360

Rev0360 completes the first actual schema-pruning cutover. The **50 zero-use `registered_unused` fields** carried since rev0357 were removed from the closed scoreboard schema, `field-registry.json`, and `field-use-ledger.json`.

Current schema count: **317 registered fields**. Current `registered_unused` count: **0 registered_unused fields**. Mechanical evidence associations remain **6793 mechanical evidence associations**.

The cutover was intentionally narrow: fields with usage count 1 or 2 remain live because a low-use field may still be conceptually necessary. See `docs/00-meta/field-retirement-cutover-audit-rev0360.json` for the retired IDs and safety tests.
