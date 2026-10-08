# tokio_broadcast_closed_still_delivers_retained_values_until_exhausted

Tokio `broadcast` documents that once all senders are dropped the channel is closed, but each receiver still gets retained values until its retained history is exhausted, after which `recv` returns `RecvError::Closed`.

This scenario exists to keep **channel closed** separate from **receiver tail exhausted**.
