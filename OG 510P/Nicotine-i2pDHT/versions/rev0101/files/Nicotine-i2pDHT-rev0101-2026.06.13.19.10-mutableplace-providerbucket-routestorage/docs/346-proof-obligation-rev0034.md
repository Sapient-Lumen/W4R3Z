# Proof obligation — rev0034

The current tests must show:

- launch quorum accepts a streaming-first, restart-safe, intent-bound leaf launch;
- local-unavailable SAM probes do not become live launch permission;
- garden/bridge mode cannot launch on session-only probe evidence;
- component replay, endpoint drift, and intent mismatch are quarantined;
- metric events reject raw keys, raw destinations, scope mismatch, and cardinality overflow;
- folded rev0033 branchlet surfaces stay audit-visible.
