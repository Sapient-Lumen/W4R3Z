# Network topology + firewall as derived operations (no rc.conf folklore)

Networking is one of the most common sources of **silent drift** in real fleets:

- an emergency `ifconfig` / route tweak that never makes it back to config
- a pf rules hotfix applied by hand and later overwritten
- DHCP/RA/WiFi state scattered across tools
- “it worked before the reboot” mysteries

DeriveBSD already treats **egress** and **listening** as brokered capabilities.
But **the substrate** (interfaces, bridges, addresses, routes, pf root ruleset + anchor attachment points)
also needs to be planned, receipted, and drift-checked.

Greenfield advantage: make **network mutation** a first-class “derived operation”, so the answer to

> “what changed about networking?”

is always: “here is the plan digest, here is the receipt, here are the diffs.”


## Stance

1) Host networking has a **typed intent**:
- `net.topology.plan`

2) Applying networking emits a **typed receipt**:
- `net.topology.receipt`

3) Drift and denied writes are **typed events**:
- `net.topology.event`

4) The actual rule/asset bodies live as **artifacts** in the store.
Plans/receipts reference them by digest:
- pf root ruleset digest
- per-instance anchor rule digests (or compiled templates)
- optional table entry digests


## What belongs in a topology plan

A topology plan should be *boringly minimal* and focus on:

- link objects: bridges, taps/epairs, VLANs, loopbacks, optional WireGuard
  - optional backend: netgraph fabrics (graph-shaped datapaths)
  - optional accelerator: netmap/VALE for specific high-rate switching paths
- addressing: static addresses and aliases (or a “DHCP by broker” declaration)
- routing: default route and any required static routes
- pf posture: pf enabled/disabled, root ruleset digest, anchor digests

Non-goals (v1):
- WiFi UX and roaming policies (adapterized later)
- “network manager” state machines inside the core


## pf integration (anchors remain the unit)

DeriveBSD already treats pf anchors as the unit of per-instance firewall policy.
The topology plan makes this **operable**:

- root ruleset is tiny and stable (baseline defaults + Derive attachment points)
- per-instance anchors are loaded/replaced atomically
- anchor names and rule digests are included in `net.topology.receipt`

See: `docs/67-pf-anchors-per-instance.md`, `adrs/ADR-0017-pf-anchors-unit.md`.

## Optional netgraph/netmap fabrics (backend lanes)

DeriveBSD's default posture should remain **simple**: `if_bridge`/`epair` + pf anchors.

But some deployments want a **graph-shaped datapath** (wiring as a first-class object) or a **high-rate switching** fast path. FreeBSD's netgraph and netmap/VALE provide these as *optional* substrates.

Design stance:

- netgraph/netmap are *implementation backends* for `net.topology.plan` (not separate configuration systems)
- they are **policy-gated** (kernel modules + node allowlists)
- apply emits receipts that include a **graph snapshot digest** and node/type inventory
- enabling them must be visible in drift bundles and closure diffs (it changes the attack surface)

See: `docs/400-netgraph-and-netmap-as-derived-network-fabrics.md`.


## Commit-confirmed networking (avoid remote bricks)

Network changes are a classic remote-brick vector.
DeriveBSD should support commit-confirmed semantics for risky plans:

- apply topology
- require an explicit confirmation within TTL
- if confirmation is missing, automatically rollback to last-known-good

This can be implemented using the existing confirmable change-set lane,
with network receipts linked into the parent change receipt.


## Drift checking

A drift checker can periodically compute an **observed network state digest** (digest-first):

- link inventory (names + types + selected parameters)
- address set
- route set
- pf enablement + root rules digest + loaded anchors digests

If observed != planned:
- emit `net.topology.event` with action `drift-detected`
- optionally block promotions or require maintenance leases to proceed


## Relationship to the broker lanes

- The egress broker and listen broker remain the *workload-facing* authority boundaries.
- `net.topology.plan` is the *host substrate* contract.

In other words:
- brokers decide **who may talk**
- topology decides **what exists to talk through**


## References (why this is worth baking in)

- Declarative networking has proven it reduces drift and improves operability:
  - systemd-networkd’s `.netdev` / `.network` model
  - NixOS’s “networking is configuration” posture

- FreeBSD’s historical rc.conf/ifconfig model works, but it does not automatically produce
  auditable receipts; DeriveBSD can keep the primitives while upgrading the lifecycle.

See: `docs/32-curated-references.md`.


Last updated: 2026-02-27r115
