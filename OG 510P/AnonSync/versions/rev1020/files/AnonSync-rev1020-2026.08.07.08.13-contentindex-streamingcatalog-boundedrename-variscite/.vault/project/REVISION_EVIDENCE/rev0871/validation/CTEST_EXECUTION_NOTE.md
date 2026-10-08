# Registered-test execution note

The final registry contains 174 tests. The parallel all-registry invocation
observed 173 passing tests and had started test 31,
`anonsync_core_sync_domain_model_selftest`, when the command execution window
ended. The process was not reported as a test failure. The exact remaining test
was then executed by registry index in isolation and passed. Thus 174/174
registered tests are covered with no failure, but one uninterrupted 174-test
invocation is not claimed.

Tests 51 through 103 are the 53 registered source/structure audits. They were
also rerun as a dedicated final-source lane and passed 53/53.
