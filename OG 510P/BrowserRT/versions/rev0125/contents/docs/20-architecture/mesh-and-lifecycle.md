# Same-origin mesh and lifecycle

The related-work pass elevated cross-tab coordination from a late feature to an
early architectural assumption.

## Mesh idea

A single origin can have many live agents:

- a visible page running interactive UI;
- hidden pages with stale or background state;
- dedicated workers owned by pages;
- a shared worker coordinator where available;
- a service worker bridge for cache/network/install lifecycle;
- worklets for specialized audio/render cases in future revisions.

BrowserRT should assume agents can join, leave, crash, reload, hide, become
visible, or be throttled.

## Coordination tools

BrowserRT should eventually combine:

- Web Locks for exclusive same-origin jobs and leader election;
- BroadcastChannel for pub-sub notifications;
- SharedWorker for a coordinator agent where supported;
- MessageChannel for direct pipes;
- service worker messages for cache/network lifecycle;
- OPFS manifests for durable state and recovery.

## Early design constraints

Even before implementation, protocols should include:

- agent ID;
- boot ID;
- revision ID;
- capability profile;
- visibility state;
- leadership epoch;
- heartbeat timestamp;
- clean shutdown versus lost heartbeat;
- trace sink route.

## Lifecycle states

```txt
cold
  -> booting
  -> joined
  -> calibrated
  -> active
  -> degraded
  -> draining
  -> closing
  -> lost
```

A later implementation can simplify, but the message envelope should not block
these states.

## Leadership examples

- storage compactor leader;
- OPFS manifest writer;
- trace recorder;
- service-worker upgrade coordinator;
- background precompute worker;
- runtime devtools inspector.

## Non-claims

The mesh is same-origin coordination, not distributed consensus. It does not
coordinate across users, devices, browsers, origins, or servers.
