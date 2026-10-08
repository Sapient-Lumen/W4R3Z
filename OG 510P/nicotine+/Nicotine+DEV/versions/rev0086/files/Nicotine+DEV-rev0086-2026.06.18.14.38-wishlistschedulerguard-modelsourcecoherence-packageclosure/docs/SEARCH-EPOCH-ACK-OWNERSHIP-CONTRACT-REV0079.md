# Search epoch acknowledgement and ownership contract — rev0079

## Four boundaries that must not be collapsed

```text
main enqueue acceptance
  the producer placed a command in a local queue call

network command observation
  the network thread dequeued and began validating the command

network output ownership
  every prepacked request is in network-owned server output state and matching
  response admission has been applied

remote progress
  bytes were written, received, processed, and perhaps answered
```

Only the third boundary can support a local `epoch-applied` event. It is still not remote completion.

## Failure-atomic fan-out

Buddy and multi-user searches generate one `UserSearch` server message per recipient. The transaction unit must therefore be the complete recipient fan-out, not the first message or a single envelope describing many peers.

Before any success event, the network side must establish all of these facts:

```text
transaction and generation still current
server session permits the requests
recipient set is nonempty where the mode requires recipients
recipient identities are unique under the chosen epoch policy
all messages can be packed
all packed messages can be staged together
old/new response-admission transition completed
```

A single un-packable or otherwise invalid recipient request rejects the whole epoch and leaves the old page/token/result set intact.

## Why current helpers cannot simply be wrapped

`_process_outgoing_messages()` can return early when queue processing is disabled or a server message is not permitted. It can skip closed connections. `_process_server_output()` returns silently when packing yields no content. Neither reports a per-message result to its caller.

Consequently, this pattern is invalid:

```text
_process_outgoing_messages(epoch_messages)
emit epoch-applied
```

The caller cannot know that every message reached output ownership. A production experiment would need an explicit fail-closed result contract or a dedicated transaction path that pre-packs all messages before committing any state.

## Event ordering

The current network loop drains queued commands before processing ready sockets. A dedicated transaction can therefore stage output bytes, queue `epoch-applied`, return, and only then permit socket read/write processing in that loop iteration. A response caused by the new request cannot legitimately overtake the acknowledgement in the network-to-main FIFO.

The main thread must still match all of:

```text
logical search ID
transaction ID
generation
old token
new token
```

Duplicate, stale, mismatched, or closed-page acknowledgements are ignored. New-token results observed while the epoch is still pending fail closed.

## Disconnect matrix

```text
disconnect before enqueue
  reject immediately; retain old page and route

disconnect after enqueue but before network observation
  queue drain loses command; disconnect event aborts pending epoch

disconnect during transaction application
  no event-loop interleave should occur inside one network-thread command;
  ordinary exceptions still require rollback

disconnect after output ownership but before main acknowledgement delivery
  FIFO normally delivers applied then disconnected; product policy decides whether
  to keep the committed empty page, restore stale rows, or mark failure

disconnect after socket write
  remote receipt remains unknown; same product policy is still needed
```

## Recommended research direction

The next experiment should preserve an undo/stale snapshot beyond the local acknowledgement and compare three explicit policies: immediate clear, stale-view swap on first fresh result, and generation-aware replay after reconnect. No policy should be hidden inside queue plumbing.
