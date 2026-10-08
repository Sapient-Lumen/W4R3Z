# Telemetry debt retention

`metricsveil.py` made metrics emission less leaky.  `telemetrydebt.py` handles the next boundary: retained diagnostics are still local state and metadata.

The debt model checks:

- raw leaked fragments must not survive into retention;
- batches must not mix scopes unless explicitly allowed;
- per-item cardinality must fit the local budget;
- retained byte budget must not grow without GC pressure;
- telemetry that summarizes hard-negative evidence must not outlive the evidence itself.

The purpose is operator feedback without turning diagnostics into a side-channel archive.
