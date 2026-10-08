# tokio_watch_closed_keeps_last_value_and_can_reopen_via_subscribe

Tokio `watch` documents that `changed` errors only when the channel is closed and the current value is already seen, while `Sender::closed` says the channel can be reopened by `subscribe`.

This scenario exists to keep **closed interval** separate from **permanent terminal state**.
