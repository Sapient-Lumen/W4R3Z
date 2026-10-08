# tokio_watch_latest_snapshot_silently_discards_intermediate_sequence

Tokio `watch` documents that only the last sent value is made available to receivers and that all intermediate values are dropped.

This scenario exists to keep **latest-state visibility** separate from **ordered message history**.
