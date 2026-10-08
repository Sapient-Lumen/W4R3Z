# CTest execution note: AnonSync rev0868

The registry contains 170 tests. `anonsync_core_sync_domain_model_selftest` is
declared `RUN_SERIAL` and owns the integration-scale sync-domain fixture.

Release evidence uses two explicit lanes:

1. 169 nonserial tests under `ctest -j8`, all passing; and
2. the declared serial owner in an isolated CTest invocation, passing and
   reporting 611/611 internal assertions in its direct executable run.

This preserves the established cloud-container evidence model. A single
uninterrupted 170-test CTest invocation is not claimed because prior revisions
observed wrapper stalls when the serial fixture owner launched immediately
following the parallel lane, while isolated CTest and direct execution remained
clean.
