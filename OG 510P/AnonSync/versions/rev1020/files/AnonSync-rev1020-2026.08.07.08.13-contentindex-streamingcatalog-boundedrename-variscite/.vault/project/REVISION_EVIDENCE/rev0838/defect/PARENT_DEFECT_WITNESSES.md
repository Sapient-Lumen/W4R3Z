# Parent defect witnesses

The rev0837 heartbeat file was read through the hardened opened-object boundary, but the bytes were then interpreted by permissive domain-local policy. That split created several authority errors.

1. **Unproved finality bypassed lifecycle checks.** After format/path/session checks, a JSON `final=true` returned success before proving a recognized state, a released durable owner generation, or a service-instance binding (`parent-heartbeat-preflight.slice.cpp`, parent lines 11381-11417).
2. **The stale horizon was trusted, not derived.** `stale_at_epoch` was accepted as an independent number; no exact-range or `heartbeat_epoch + stale_after_seconds` relation was proved. A contradictory document could therefore move takeover earlier or later.
3. **Owner evidence was observationally read but not bound.** The parent extracted only `owner_lock_id` and did not match daemon, worker, epoch, acquisition, expiry, release state, and release epoch to the durable row before re-entry.
4. **Release failure could still mint final evidence.** The failure finalizer caught owner-release failure and then serialized state `failed` with `final=true`. That advertised completion while the durable owner could remain live.
5. **Status and preflight disagreed.** The status path could suppress malformed or fresh non-final heartbeat attention when the durable owner was no longer live, even though a new daemon preflight would refuse the same file.
6. **Service identity was shape-like, not relational.** The digest-shaped `service_instance_id` was not recomputed from session, daemon, worker, and restart material.

rev0838 does not make heartbeat bytes a standalone capability. It validates their internal meaning and then binds them to exact domain and durable-owner evidence at the consuming boundary.
