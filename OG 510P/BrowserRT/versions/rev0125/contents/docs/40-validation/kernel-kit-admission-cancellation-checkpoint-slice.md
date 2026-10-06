# Kernel Kit Admission/Cancellation Checkpoint Slice — rev0107

Tasks: `demo:kernel-kit-admission-cancellation-checkpoint-proof` and `admission:abort-release-proof`.

The checkpoint turns bounded admission cancellation into Kernel Kit evidence rather than a loose controller behavior. It ranks high-risk rows for pre-aborted no-mutation rejection, AbortSignal lease release, dual-signal composition, listener detach after manual release, low-watermark recovery, post-abort background admission, and local rejection of invalid signal shapes.

The default support bundle intentionally keeps the release-light admission abort-release rows deferred until the proof artifact is run. That means `admission-cancellation-backpressure-evidence` is visible in the lifecycle checkpoint without implying that every caller, provider, Worker, or browser lifecycle has cancellation coverage.

Non-claims: no exactly-once execution, no task preemption, no provider rollback, no Browser Worker cancellation, no cross-browser or mobile cancellation conformance, no fairness/latency/SLO claim, and not production cancellation readiness.

The pre-aborted row uses a no mutation assertion so a cancelled caller cannot allocate a hidden lease.
