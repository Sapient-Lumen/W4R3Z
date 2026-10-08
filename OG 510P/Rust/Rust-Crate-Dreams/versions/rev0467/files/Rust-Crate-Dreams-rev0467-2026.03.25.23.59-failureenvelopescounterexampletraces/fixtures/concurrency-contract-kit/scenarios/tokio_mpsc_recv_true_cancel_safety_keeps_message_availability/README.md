# Tokio `mpsc::Receiver::recv` true cancel safety keeps message availability

This scenario exists to show that cancellation can preserve buffered messages.

`recv` documents that cancellation in a `select!` race does **not** receive a message.
The fixture protects against collapsing queue withdrawal and message-preserving cancel safety into the same class.
