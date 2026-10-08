# rev0120 audit — challenge receipt portability refactor

## Scope

The audit targeted authorized-verifier challenge/result records because rev0119 left replay/portability chains as the next high-value mutation frontier. The pass focused on mutations that preserved the object shape while weakening the actual verifier-result meaning.

## Closed survivors

1. Result-bearing records can no longer be relabelled as plain `authorized_verifier_challenge` records.
2. Top-level challenge result outcomes now have to match their disclosure-row outcomes.
3. Salt/preimage verifier records cannot be reinterpreted as external-system or selective-disclosure receipts by changing one enum.
4. External preimage review receipts must bind `authorized_verifier_challenge_receipt`.
5. A `not_portable` or `not_replayable` portability boundary cannot advertise replay uses.
6. Verified disclosure rows must point at the digest value of the receipt attached to the result.

## Refactor notes

The new `tools/authorized_verifier_result_semantics.py` keeps non-temporal result semantics separate from `tools/authorized_verifier_temporal.py`. That avoids growing the temporal helper into a mixed semantic bucket, while also keeping `tools/validate_archive.py` from gaining another long block of challenge-result checks.

The validator still owns profile-resolution and nested evidence-summary checks. The new helper owns only local result consistency: record kind, authorization binding, salt/preimage receipt alignment, result/disclosure consistency, and portability boundary contradictions.

## Remaining risk

The next meaningful frontier is evidence-summary role drift. A broad exploratory scan still shows that some `used_for` mutations can survive when item names stay present and usable. That should be handled carefully because some positive fixtures intentionally carry unused or explanatory items; the next pass should distinguish current satisfied witnesses from not-used comparison material before tightening roles.
