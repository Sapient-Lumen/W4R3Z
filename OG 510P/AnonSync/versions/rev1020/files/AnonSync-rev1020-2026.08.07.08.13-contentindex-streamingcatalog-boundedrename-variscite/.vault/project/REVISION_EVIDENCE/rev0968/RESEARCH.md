# Research notes — rev0968

Continuation identity belongs in the request, not only in diagnostics returned after several pages have already been combined. Syncthing's Block Exchange Protocol uses retained index identity and sequence cutpoints to make continuation state explicit; AnonSync's local token binds different inputs but follows the same broad principle that a continuation must name its source.

SQLite read transactions demonstrate stable observation inside one database connection, but the replica and rooted payload store are distinct owners. Rev0968 therefore uses an explicit cryptographic bracket: compare the operation set before the payload scan, observe the full payload namespace, compare the operation set again, and then compare the payload snapshot. It does not describe that bracket as one transaction.

Generic generations are attractive but over-broad. A token that advances on unrelated liveness writes creates false pagination failures. The digest should cover exactly the immutable causal operation set that determines projection, while the independent payload digest covers restore availability.

The sanitizer-only oracle failure was also a useful systems lesson: stable action history and transient generic scheduler telemetry have different lifetimes. Tests must poll the retained domain for retained facts and use `last_step` only when its generation proves it is the relevant step.

The next product edge is still deliberate history lifecycle policy: pins, current/version/in-flight reachability, bytes/count/age limits, crash-safe mark/quarantine/revalidate/unlink collection, friendly ordering metadata, conflict copies, and restore UX measured against a named Resilio workflow.
