# rev0838 next-work compass

1. **Bind process incarnation.** Replace the observational PID-only field with the existing process-incarnation boundary (PID plus platform start identity/boot context where available), and recompute that relation during preflight and status.
2. **Extract one lifecycle decision function.** Preflight and operator status share the decoder but still contain parallel branch choreography. Move freshness/finality/attention classification into a pure typed policy so the two consumers cannot drift again.
3. **Narrow the serializer input.** The leaf links independently, but its implementation still includes the large internal umbrella for daemon options/result definitions. Introduce an immutable `HeartbeatPublicationView` containing only the fields the serializer owns.
4. **Define lockless trust explicitly.** With durable owner fencing disabled, a local file can influence re-entry more directly. Either authenticate the document, make lockless heartbeat advisory-only, or remove takeover decisions from that mode.
5. **Version the schema.** The v1 document retains historical `revision_id: rev0741`. Define schema-version semantics and a migration/compatibility policy rather than allowing source revision labels to masquerade as protocol versions.
6. **Model suspicion separately from authority.** A stale wall-clock deadline is a failure-detector hint. Introduce explicit suspected/stale/retired states and test clock rollback, large forward jumps, restart, PID reuse, and concurrent observers.
7. **Crash-cut the publication protocol.** Reuse the atomic-publication cutpoint machinery to test heartbeat temp creation, data sync, rename, directory sync, owner release, and restart as one cross-resource recovery protocol.
8. **Build Windows.** The typed leaf is portable C++, but this cloudtainer did not compile or execute Windows filesystem/process-incarnation paths.

The next high-return architectural target remains the 15,240-line `sync_domain.cpp`: extract one invariant owner at a time, with a no-core focused proof and byte/behavior parity, rather than slicing by arbitrary size.
