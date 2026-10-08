# rev0034 audit/refactor notes

Added `tools/exactness_guard_report.py`. It scans current-revision probe outputs for exact-copy, needle, reachability, target-miss, rare-token, route-flip, and related guard fields. This is a performance-promotion report, not a security audit.

The report exists because many efficient mechanisms can look good on averages while failing exact evidence recovery.
