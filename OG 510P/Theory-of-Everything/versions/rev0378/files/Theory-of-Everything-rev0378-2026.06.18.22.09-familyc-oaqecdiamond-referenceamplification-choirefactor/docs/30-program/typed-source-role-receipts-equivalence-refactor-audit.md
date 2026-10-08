# Typed source-role receipts and equivalence-principle refactor audit (rev0346)

Current linked revision: `rev0346` (`typed-source-role-receipts-ep-refactor`). Bundle: `Theory-of-Everything-rev0346-2026.06.09.12.10-typed-source-role-receipts-ep-refactor.zip`.

## Why this was the risky area

The riskiest failure mode was not missing prose. It was source-role leakage: fresh public records about equivalence-principle tests, fifth-force searches, inverse-square-law limits, cold-atom WEP tests, and ACES/PHARAO clock operations could be read as current scientific support unless the archive made their role executable. The rev0344 pass had the right scientific boundary, but much of it lived in per-row `rev0344_*` note keys and human narration.

## Changes made

`FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` is now schema_version `1.1`. Every assertion row has `source_role`, `checked_at`, `public_status`, and `no_promotion_disposition`. Optional `secondary_source_roles` and `source_snapshot_receipts` allow one assertion to document live public records without creating acquired support.

`FSF-0032-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-SOURCE-ROLE` now has snapshot receipts for REF-0437, REF-0725, REF-0726, REF-0727, and REF-0728. Their disposition is explicit: these records are denominator pressure or operational-status receipts only, capped at S0.

`EQUIVALENCE-PRINCIPLE-LEDGER.json` was refactored from ad hoc per-revision note keys into `source_role_events`. Non-metadata equivalence rows now carry denominator-pressure events covering the equivalence/fifth-force/weak-field refs with `credit_cap: S0`. The metadata-provenance wrapper carries a metadata-wrapper event and does not carry the pressure refs.

`tools/lint_archive.py` now enforces the new boundary: equivalence-principle rows may not retain `rev####_*note` keys, must carry normalized `source_role_events`, must cap denominator-pressure events at S0, and may not let metadata wrappers carry the equivalence/fifth-force pressure refs. It also rejects stale `Current linked revision:` lines on the high-salience navigation surfaces.

## Audit/refactor result

The refactor removed the highest-risk ad hoc note-field pattern from the equivalence-principle ledger and made it a replayable source-role event structure. This is forward momentum because the next migration target is now mechanical: repeat the same event conversion for weak-field/PPN, classical-GR observed-sector, and QM/QFT denominator ledgers that still have revision-note accretion.

## Non-promotion boundary

No route is promoted. Freshness, launch, mission-operation, review, and improved-limit records can raise denominator burden or repair custody, but they cannot become acquired route-native support without a separate acquired evidence-unit row and route-local scoring pass.

## Next risky work

The next pass should extend the event migration outside equivalence-principle rows and compress generated chronology out of stable navigation surfaces. That is more valuable than creating another broad registry because the leak now lives in remaining family-local source-role accretion and stale navigation salience.
