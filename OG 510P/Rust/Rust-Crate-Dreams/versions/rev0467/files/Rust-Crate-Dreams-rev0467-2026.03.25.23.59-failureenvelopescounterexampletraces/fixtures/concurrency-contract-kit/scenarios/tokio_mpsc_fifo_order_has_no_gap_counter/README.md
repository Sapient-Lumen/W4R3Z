# tokio_mpsc_fifo_order_has_no_gap_counter

Tokio bounded `mpsc` documents single-consumer FIFO delivery: all data sent on `Sender` becomes available on `Receiver` in the same order as it was sent.

This scenario exists to keep **ordered queue delivery** separate from **counted gap visibility**. FIFO is real here, but the docs do not export a special skipped-message counter analogous to broadcast lag accounting.
