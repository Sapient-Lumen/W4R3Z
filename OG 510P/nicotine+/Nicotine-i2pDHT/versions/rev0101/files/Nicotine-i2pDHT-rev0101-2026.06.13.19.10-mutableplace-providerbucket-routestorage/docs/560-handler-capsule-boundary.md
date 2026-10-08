# Handler capsule boundary

The handler capsule is the inbound side of the public edge. It exists because `liveadapter` can say a future handler path is rehearsed, but that still does not say the handler itself may run.

A handler capsule binds:

- mode and handler work kind;
- profile and service;
- scope and request;
- inbound payload digest;
- caller digest and handler digest;
- profile-edge, live-adapter, ingress-drain, and backpressure report digests;
- metadata, raw-key, handler budget, and hard-negative counts;
- sequence, previous digest, time window, family, path family, and signature.

The risky failures are exact-boundary failures: a valid report for the wrong caller, wrong handler, wrong payload, wrong request, or wrong component must not authorize work.

The boundary is still no-network. It does not execute handlers. It creates local proof pressure before handler execution exists.
