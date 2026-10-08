# std_mpsc_disconnect_is_drain_then_terminal_with_buffered_tail

`std::sync::mpsc::Receiver` documents that if the sender disconnects, buffered messages sent before disconnect can still be properly received, after which `RecvError` indicates that no more values can ever be received.

This scenario exists to keep **sender disconnected** separate from **receiver immediately terminal**.
