# Scenario — retries, stress, and fail-fast change attempt topology

A final PASS or FAIL line is not enough when tests are retried, run under stress mode, or stopped early by fail-fast policy.
This scenario exists to keep the verdict separate from the attempt topology that produced it.
