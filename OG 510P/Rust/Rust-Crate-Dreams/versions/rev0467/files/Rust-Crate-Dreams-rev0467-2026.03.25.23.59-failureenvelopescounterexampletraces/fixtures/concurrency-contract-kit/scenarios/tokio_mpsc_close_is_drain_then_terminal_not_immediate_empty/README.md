# tokio_mpsc_close_is_drain_then_terminal_not_immediate_empty

Tokio `mpsc` documents clean shutdown as `close` plus draining to completion. The receiver docs also say buffered messages remain receivable and outstanding permits may still yield values.

This scenario exists to keep **receiver-side closure** separate from **immediate emptiness** or **proof that no values remain**.
