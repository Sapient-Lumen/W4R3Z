# chrony replay and capture fixtures

These fixtures are sanitized `chronyc tracking`, `chronyc sources`, and `chrony_command_capture_v1` examples used by `tools/chrony_adapter.py` and `tools/chrony_capture.py`. They are not a claim about this cloud container's current clock. They preserve chrony's operational field names so the parser is exercised against the same human-readable surface operators actually inspect.

rev0123 adds `tests/fixtures/chrony/capture-normal.json`, which wraps the normal replay fixture with deterministic wall-clock and monotonic capture brackets, command roles, command arguments, command outputs, and unsupported/not-verified statements.

The first adapter intentionally uses only `tracking` plus optional `sources`: enough to derive a conservative current-time interval and a P1 profile decision, not enough to claim UTC traceability, NTS verification, leap-smear knowledge, chrony configuration correctness, or cross-vendor NTP/PTP interoperability.
