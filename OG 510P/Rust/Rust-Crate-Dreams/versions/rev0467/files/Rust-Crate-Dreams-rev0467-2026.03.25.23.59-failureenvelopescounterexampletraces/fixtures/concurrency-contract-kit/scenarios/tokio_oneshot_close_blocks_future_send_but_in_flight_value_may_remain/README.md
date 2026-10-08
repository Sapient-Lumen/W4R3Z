# tokio_oneshot_close_blocks_future_send_but_in_flight_value_may_remain

Tokio `oneshot::Receiver::close` documents that future sends will fail, but `try_recv` should still be used to recover a value that may have been sent before `close` completed. The module docs also say an already-sent value can remain until the receiver is dropped.

This scenario exists to keep **close succeeded** separate from **no value remains recoverable**.
