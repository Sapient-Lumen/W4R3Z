# Live adapter no-network boundary

`liveadapter.py` is the rev0052 rehearsal seam before a future implementation can run a public-edge side effect.

It models three modes:

```text
outbound_public_send
inbound_handler_work
bidirectional_bridge_tick
```

A live adapter plan binds:

```text
profile/service
scope/request
payload/frame
session/Destination
caller/handler
router canary digest
ingress drain digest
backpressure digest
effect ledger digest
sequence/previous digest
time window
family/path family
signature
```

The risky guess pinned in tests is that component success is not enough. A bidirectional bridge tick must carry both router and ingress evidence. An outbound send must not smuggle an ingress digest. An inbound handler plan must not smuggle an effect-ledger digest. Backpressure mode must match adapter mode.

This surface still does not open sockets, write to SAM, or call handlers.
