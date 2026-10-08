# Portable bundle composition should keep concurrency claims separate

A receiver-facing support bundle should inventory its component reports instead of compressing them into one verdict.

This bundle may now also include an optional `failure-recovery.report.json` when panic/recovery posture is relevant.
