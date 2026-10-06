# DNS mediation + hostname binding (avoid TOCTOU and make name lookups auditable)

Networking policy frequently uses **hostnames** ("allow api.example.com:443") but the enforcement point
(`connect()` to an IP) operates on **addresses**.

Without a first-class design for name resolution:
- hostnames in policy become **folklore** or a leaky convenience
- DNS becomes ambient authority again (`/etc/resolv.conf` + raw sockets)
- incidents cannot answer "what name resolved to what address at the time of this connection?"

DeriveBSD already has the correct direction:
- outbound traffic is brokered (`system.net`)
- DNS is a mediated capability (Casper adapter)

This note tightens that into a **receipt-bearing** lane.

## Prior art worth stealing

- FreeBSD **Casper** exposes DNS as a capability-mode service (`system.dns`) usable via `cap_dns`.
  - cap_dns(3): https://man.freebsd.org/cgi/man.cgi?query=cap_dns&sektion=3

## DeriveBSD primitives

- `net-egress-grant` already includes `dns_lookup` permission.
  - Schema: `spec/net.egress.grant.schema.json`

Add a companion evidence object:

- `net-dns-query-receipt` (signed): records DNS queries performed under a grant (or under a unit’s resolved DNS policy).
  - Schema: `spec/net.dns.query.receipt.schema.json`

And tighten `net-flow-receipt` to optionally reference name-resolution provenance:
- optional `hostname`
- optional `dns_query_receipt_digest`

See: `spec/net.flow.receipt.schema.json`.

## Model: broker-resolved hostnames

### 1) Policy uses hostnames, broker enforces addresses

If a unit requests a flow for `api.example.com:443`:

1) unit must hold `net-egress-grant` with a matching hostname rule
2) unit asks `system.net` to open a flow to that hostname
3) `system.net` resolves the name *via a mediated DNS capability* (Casper `system.dns` or an internal DNS sub-API)
4) `system.net` binds the flow to the resolved address set and opens the connection
5) the plan/receipts record:
   - the DNS query receipt digest
   - the chosen address
   - the hostname asserted for that flow

This turns "hostname allowlists" into a real, checkable enforcement path.

### 2) TOCTOU control

If DNS is resolved outside the broker, policy becomes vulnerable to:
- last-second DNS changes
- local resolver state manipulation
- differences across processes

Broker-resolved DNS allows a tight invariant:
- *every* hostname-based connection is bound to an evidenced resolution step

## Privacy + budgets (DNS can be sensitive)

DNS receipts can leak:
- internal hostnames
- browsing/traffic patterns

So we treat DNS mediation as part of the authority budget lane:
- per-unit budgets (query rate, retention)
- redaction classes (hash hostnames, drop qname, or keep full detail)
- export requires `export.policy` mediation

The product-shape default is now fixed more narrowly in `docs/504-dns-receipt-detail-and-export-posture-by-profile.md`: `net-flow-receipt` stays the normal export/review surface, detailed DNS receipts stay local-first and bounded, and off-box qname disclosure becomes progressively harder from A→D.

See: `docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/195-deterministic-redaction-transforms.md`.

## Implementation sketch (FreeBSD-first)

- Use Casper `cap_dns` / `system.dns` as the day-0 adapter for capability-mode components.
- `system.net` provides a small RPC surface:
  - `resolve(name, type)` → `answers + receipt_digest`
  - `open_flow(hostname|ip, proto, port)` → `flow_handle + flow_receipt`

The internal transport remains flexible:
- VNET, NAT, proxy, or per-compartment resolver stubs are all implementation details.

## Wiring

- `docs/201-network-egress-as-capability.md`: treat DNS mediation as a mandatory path when grants use hostnames.
- `docs/286-inbound-listen-broker-and-firewall-leases.md`: inbound rules that use names (rare) should also use the resolver lane.
- Component descriptors (`derive.unit`): declare DNS intent (none / brokered / restricted resolvers) so the Plan compiles the right enforcement.

## Open questions

- Do we require brokered DNS for *all* outbound flows, or only those configured with hostname rules?
- What exact deterministic transform vocabulary should exported DNS evidence use for public vs split-horizon/internal names?
- What promotion rules should move a lane from normal flow evidence to richer per-query DNS detail during learn/audit or incident response?

Last updated: 2026-03-08r233
