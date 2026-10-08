# Tokio `Notify` queue loss is not channel message loss

This scenario exists to keep **P-0538** honest about cancellation.

`Notify::notified` documents fair queueing and says cancellation loses queue place.
It also documents stored-permit behavior for `notify_one`.

The fixture protects against collapsing all of that into one vague “cancel safe” or “message lost” statement.
