# tokio_broadcast_per_receiver_fifo_exposes_lag_counts

Tokio `broadcast` documents that each active receiver sees sent values in the same order they were sent. It also documents `RecvError::Lagged(u64)` and cursor rebasing to the oldest retained value.

This scenario exists to keep **per-receiver FIFO** separate from **all-history retention** and from vague claims like “messages may be lost.”
