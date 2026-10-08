# Reachability lineage receipt page: discovery basis, route witness, and exposure ceiling interface spec

Every network-reachability decision that materially affects connectivity claims or privacy claims must emit one durable receipt.
This receipt is the audit answer to:

> how was this peer found, what route was actually witnessed, what outside infrastructure was contacted, what fallback remained allowed, and what stronger sentence stayed blocked?

## Receipt fields

- `reachability_receipt_id`
- `reachability_contract_id`
- `subject_ref`
- `peer_ref`
- `discovery_basis`
- `discovery_evidence[]`
- `current_route_class`
- `route_witness[]`
- `service_contacts[]`
- `exposure_verdict`
- `fallback_ladder[]`
- `performance_ceiling`
- `privacy_ceiling`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `issued_at`

## Human-readable layout

### 1) Discovery summary

State in one sentence how the peer was introduced.

Example:

- `Peer was introduced by tracker and later moved onto a direct WAN route.`

### 2) Route witness

List the witness classes that justify the current route claim and keep stale or contradictory witnesses visible.

### 3) Service-contact exposure

List which outside services were contacted and what data classes each service could see.

### 4) Fallback ceiling

Show what still remains allowed after the current state:

- relay still allowed
- tracker still allowed
- predefined hosts still armed
- LAN rediscovery still armed
- no remaining fallback

### 5) Blocked stronger sentence

Keep the strongest forbidden sentence permanently adjacent to the receipt.

Example:

- `Blocked: no third-party service learned anything about this share or its peers.`

## Example compact receipt rows

```text
tracker-introduced     direct WAN currently witnessed     tracker saw share-introduction metadata     relay still allowed     blocked: direct-only private route
```

```text
predefined-host-introduced     no current route witness     no tracker contact witnessed     relay disabled     blocked: peer is presently reachable
```

```text
mixed discovery     relay-carried route witnessed     encrypted payload carried by relay     tracker historical contact present     blocked: zero third-party carriage
```

## Rules

### Rule 1 — receipts must separate discovery from transport

Do not let `relay` erase tracker introduction or let `tracker` imply direct transport.

### Rule 2 — receipts must separate metadata exposure from content exposure

A relay that cannot read content is still not the same as zero third-party carriage.

### Rule 3 — later directness does not erase earlier exposure

A direct route now does not cancel the fact that tracker or relay contact may already have occurred.
