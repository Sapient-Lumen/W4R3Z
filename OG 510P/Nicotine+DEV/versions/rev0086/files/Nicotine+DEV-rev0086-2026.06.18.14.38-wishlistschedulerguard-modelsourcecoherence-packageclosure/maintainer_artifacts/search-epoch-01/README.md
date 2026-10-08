# SEARCH-AGAIN-EPOCH-01 research packet

This packet models a true replacement refresh without selecting an upstream patch.

## Identity split

```text
logical search ID
  stable page, navigation, notification, close/show, and plugin identity

wire epoch token
  replaceable request/response capability

token route
  current wire token -> stable logical search ID
```

## Model generations

```text
search_epoch_model.py
  rev0078 one-phase model: ordered enqueue, rollback, late-response barriers,
  and the accepted-then-disconnected counterexample

search_epoch_ack_model.py
  rev0079 two-thread model: pending visible state, generation/transaction ack,
  complete per-recipient fan-out, prepack rejection, output ownership, close,
  duplicate/stale event handling, and post-ack disconnect limits
```

The rev0079 model treats queue acceptance, network observation, output ownership, socket write, and remote result as separate stages. A success acknowledgement follows prevalidation/prepacking and ownership of *every* request in the epoch fan-out. It never claims remote delivery.

## Test roles

```text
test_search_epoch_ack_transaction.py
  pending-state preservation, queue/preflight/packing rejection, full commit

test_search_epoch_ack_disconnect.py
  disconnect positions, FIFO ordering, output loss after local acknowledgement

test_search_epoch_ack_counterexamples.py
  ack-before-ownership, partial fan-out, stale/mismatched acknowledgements

test_search_epoch_ack_lifecycle.py
  close/cancel, buddy audience, empty audience, and rapid-repeat policies

test_search_epoch_ack_source_ownership.py
  exact bundled-source queue, event, server-output, and reconnect witnesses
```

The five rev0078 tests remain active to preserve the earlier counterexamples and identity-owner contract.

## Current conclusion

A dedicated network transaction would need to prepack all requests, reject as a unit, apply old/new response admission, stage all bytes in network-owned output state, and emit one generation-tagged acknowledgement before ready-socket processing. Existing helpers do not expose enough success information to be wrapped safely.

Even that local boundary cannot answer what the UI should do when disconnect occurs after acknowledgement or when a fresh epoch legitimately yields zero results. No patch is selected.

All files are research-only and are not contribution material.
