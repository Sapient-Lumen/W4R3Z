# CTest execution note: AnonSync rev0869

The registry contains 172 tests. `anonsync_core_sync_domain_model_selftest` is
declared `RUN_SERIAL` and owns the integration-scale sync-domain fixture.

Release evidence uses two explicit lanes:

1. 171 nonserial tests under `ctest -j8`, all passing; and
2. the declared serial owner in an isolated CTest invocation, passing and
   reporting 611/611 internal assertions in the direct executable run.

Two earlier parallel logs are retained. The first exposed an unapproved raw
`fork()` in the new crash probe. After migration to the pinned self-exec owner,
the second exposed two dependent source audits whose exact textual inventories
still described seven campaigns. Those audits were updated to eight campaigns
and 32 total inherited/fresh process sites. The final 171-test lane is green.

A single uninterrupted 172-test wrapper invocation is not claimed; the split
model preserves the established cloud-container serial-fixture discipline.
