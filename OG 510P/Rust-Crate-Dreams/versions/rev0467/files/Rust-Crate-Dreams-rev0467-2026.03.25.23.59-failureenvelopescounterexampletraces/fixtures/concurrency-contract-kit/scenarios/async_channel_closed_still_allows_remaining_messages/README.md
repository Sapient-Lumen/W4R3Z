# async_channel_closed_still_allows_remaining_messages

`async-channel` documents that when a channel is closed no more messages can be sent, but remaining messages can still be received.

This scenario exists to keep **closed channel** separate from **drained channel**.
