# CTest execution note

The final registry contains 168 tests. The release evidence uses two lanes:

1. 167/167 tests pass with `-j8` while excluding only
   `anonsync_core_sync_domain_model_selftest`. This lane contains all 50 source
   audits and every rev0867 focused runtime test.
2. The excluded integration owner passes in an isolated CTest invocation in
   9.05 seconds and reports 611/611 internal assertions when run directly.

In this cloud container, a repeated whole-registry invocation can finish the 167
parallel tests and then stall inside CTest's wrapper while launching the declared
serial owner. The owner itself terminates cleanly in isolation and directly. No
single-uninterrupted-invocation claim is made. The product test is not weakened,
disabled, or converted into a source-only check.
