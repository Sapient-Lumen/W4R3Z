# rev0974 research and next hypothesis

A safe collector cannot be derived from “unreferenced” alone. Before any unlink exists, the next design must add durable roots for in-flight receives, mutation batches, active pass snapshots, and senders; an explicit per-share byte/count policy; a human-visible grace interval; quota and ENOSPC behavior; and a writer-fenced mark/quarantine/reobserve/unlink/restart journal.

The present planner is intentionally a diagnostic oracle only. That separation prevents a convenient status page from silently becoming deletion authority.
