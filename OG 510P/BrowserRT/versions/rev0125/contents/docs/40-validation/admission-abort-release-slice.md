# Admission Abort Release Slice — rev0107

Task: `admission:abort-release-proof`.

This release-light proof exercises `WatermarkAdmissionController.tryAdmit()` with `signal` and `abortSignal` inputs. The risk is concrete: a cancelled caller can otherwise leave admission bytes or a lease in flight, making later useful work look backpressured even after the caller has gone away.

The probe proves:

- a pre-aborted AbortSignal returns `rejected-aborted` with no mutation;
- a bound AbortSignal releases an admitted lease permit and clears congestion;
- sibling `signal` and `abortSignal` inputs compose, and the first abort releases the lease once;
- manual release detaches the abort listener so a late abort is not counted as a stale cancellation;
- invalid AbortSignal-like shapes reject locally before lease mutation;
- the trace contains `admission:abort-release`.

Non-claims remain visible: this is not exactly-once execution, task preemption, provider rollback, OPFS mutation rollback, Browser Worker cancellation, fairness, throughput, latency, or production cancellation.

This is not production cancellation.
