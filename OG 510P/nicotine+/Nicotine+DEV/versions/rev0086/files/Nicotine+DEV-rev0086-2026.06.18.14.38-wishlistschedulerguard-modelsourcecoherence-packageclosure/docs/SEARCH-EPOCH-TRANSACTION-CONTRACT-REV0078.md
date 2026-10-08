# Search epoch transaction contract — rev0078

## Identity split

```text
logical_search_id
  stable identity for page, navigation, notifications, close/show, and plugins

wire_epoch_token
  replaceable capability for one outgoing request epoch and its responses

token_route
  current wire_epoch_token -> logical_search_id
```

A page intended to survive a replacement refresh cannot be keyed solely by its current wire token.

## Minimum one-phase model

The executable rev0078 model deliberately tests the minimum immediate rollback sequence:

```text
1. Resolve the live logical search and page.
2. Allocate a fresh wire token.
3. Resolve the recipient set under an explicit epoch policy.
4. Install the new token route.
5. Switch search/page current token.
6. Retire the old token route.
7. Clear rows and per-user dedup state.
8. Try to enqueue one ordered network epoch batch.
9. Roll back steps 4–7 if enqueue is rejected.
```

The network batch orders:

```text
remove old response admission
add new response admission
send all new-epoch requests
```

This is stronger than three unrelated fire-and-forget calls, but it is not a selected design.

## Late-response barriers in the one-phase model

1. **Core-route barrier.** The old main-thread route is gone before enqueue. A response parsed before the transition, or during network-control lag, reaches the main thread but cannot route into the refreshed page.
2. **Parser-admission barrier.** Once the network batch is applied, old-token messages are rejected before full result decompression.

The core barrier closes the asynchronous interval before the network thread processes the admission change.

## Durability counterexample

Queue acceptance is not network application. On server disconnect, upstream disables and drains the outgoing queue and clears response admissions. The model demonstrates this state:

```text
main thread: new token current, old rows cleared
network: accepted batch discarded, no new token admitted, no request sent
```

This invalidates any claim that an accepted enqueue alone completes the refresh transaction.

## Candidate two-phase direction

A stronger research direction is:

```text
1. Main thread creates a pending epoch but keeps old visible state current.
2. Main thread enqueues one generation-tagged network batch.
3. Network removes old admission and adds new admission.
4. Network queues an epoch-applied acknowledgement to the main-thread FIFO.
5. Network serializes the new requests only after queuing that acknowledgement.
6. Main thread commits the token switch and clear on the matching acknowledgement.
7. Missing acknowledgements are abandoned or replayed under explicit reconnect policy.
```

The acknowledgement-before-request ordering is important: new-result events must not overtake the commit event. This direction still needs close/cancel, duplicate acknowledgement, rapid-repeat, and reconnect tests before implementation selection.

## Product policy is not plumbing

Buddy searches currently resolve the live buddy set on each send. Each new epoch must explicitly choose between:

```text
live-at-epoch audience
original-request audience
```

Likewise, replacement Refresh clears results while Retry/Merge does not. These are user-visible product decisions, not incidental dictionary operations.
