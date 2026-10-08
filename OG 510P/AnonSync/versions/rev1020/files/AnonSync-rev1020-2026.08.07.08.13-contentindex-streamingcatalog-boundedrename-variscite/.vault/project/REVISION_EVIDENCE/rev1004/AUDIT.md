# Rev1004 audit

Rev1004 removes the receiver's final unbounded staged-target SHA-256 owner turn. Exact verification advances through a 32 MiB-per-call, checksum-framed, two-slot continuation bound to the durable store identity, identity inode, complete staged inode observation, target digest and size, verified offset, generation, and provider-independent resumable SHA-256 checkpoint.

Reconciliation protocol generation 8 preserves the exact operation obligation after the final source range: the cursor does not advance, subsequent turns carry no payload bytes and open no source payload descriptor, and metadata admission waits for exact receiver-local publication. Missing, malformed, torn, foreign, or stale continuation state restarts boundedly from offset zero without truncating completed staged bytes. A digest mismatch removes the invalid staged object and continuation and publishes nothing.

The adjacent refactor removed a legacy range-carrying terminal-verifier overload, centralized post-loop observation checks, overflow-checked the fixed journal frontier, and corrected the sanitizer target graph so the new codec test is bound at both compile and final link.

The next product edge is to decouple each 32 MiB verification step from a peer round trip and complete staged-prefix namespace observation, then measure sparse multi-terabyte latency, RSS, page-cache pressure, restart, disk amplification, route latency, and ENOSPC before choosing source-manifest or durable-index work.
