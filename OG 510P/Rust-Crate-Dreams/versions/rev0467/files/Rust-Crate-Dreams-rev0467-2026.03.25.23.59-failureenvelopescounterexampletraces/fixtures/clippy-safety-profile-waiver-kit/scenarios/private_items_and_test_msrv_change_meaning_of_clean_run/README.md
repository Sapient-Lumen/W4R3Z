# Scenario: private-item and test-MSRV settings change the meaning of a “clean” run

A workspace claims strict docs and MSRV posture, but its Clippy configuration leaves `check-private-items = false` and `check-incompatible-msrv-in-tests = false`.
The run may be green while still omitting private safety docs and test-only MSRV findings.
