# Bootstrap lineage receipt page, authority source, freshness, route envelope, and blocked-stronger-sentences interface spec

## Purpose

The archive already had several receipts for mutation, launch, overlap, and service continuity.
What it still lacked was one durable receipt for discovery dependency changes:

> what later proves that bootstrap authority changed, degraded, recovered, narrowed by policy, or made some peer pairs relay-bound?

Current official Resilio docs preserve the necessary ingredients, but they do not gather them into one operator-owned record.
AnonSync should.

## Core decision

Every meaningful change to discovery bootstrap or reachability posture must emit a **bootstrap lineage receipt**.
The durable record must keep together:

- authority source before and after
- freshness/trust posture before and after
- fallback envelope before and after
- pairwise relay-inevitable deltas
- strongest safe sentence and blocked stronger sentence

The product must never leave later operators to reconstruct this change from logs, warnings, or remembered network posture.

## Fixed receipt order

Every bootstrap lineage receipt should render the same sections in the same order:

1. **Change summary**
2. **Authority delta**
3. **Envelope delta**
4. **Pairwise route delta**
5. **Safe-language boundary**

### 1) Change summary

This section should show:

- action (`refresh`, `failover`, `pin-private-authority`, `disable-public-authority`, `proxy-posture-change`, `recovery`)
- acting seat
- timestamp
- whether the change was operator-requested, policy-driven, or observed from environment

### 2) Authority delta

This section should show:

- source before/after
- trust posture before/after
- freshness before/after
- preserved cached material if any

### 3) Envelope delta

This section should show:

- fallback envelope before/after
- whether new public discovery was preserved, narrowed, or lost
- whether manual/LAN fallback remained or became primary

### 4) Pairwise route delta

This section should show:

- peers newly relay-inevitable
- peers newly direct-capable
- peers now blocked or restored

### 5) Safe-language boundary

This section must preserve:

- strongest safe sentence
- blocked stronger sentence
- explanation of why the stronger claim was refused

## Public objects

### `bootstrap_lineage_receipt`

Fields:

- `bootstrap_lineage_receipt_id`
- `seat_ref`
- `action`
- `origin`
- `before_authority_summary`
- `after_authority_summary`
- `before_envelope_summary`
- `after_envelope_summary`
- `pairwise_route_delta_summary`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `created_at`

## Main surface

A compact row should read like one of these:

- `bootstrap recovered · public discovery envelope restored`
- `public bootstrap lost · manual/LAN fallback retained`
- `proxy posture accepted · relay inevitable with 2 peers`
- `private authority pinned · public dependency removed`

## Event language

Use phrases such as:

- `bootstrap authority narrowed from public catalog to manual static endpoints`
- `cached endpoint residue preserved limited continuity after fetch failure`
- `egress-only posture made relay inevitable for selected peers`
- `public discovery envelope restored after bootstrap refresh`

Avoid phrases such as:

- `network fixed`
- `tracker issue resolved`
- `proxy enabled successfully`

Those lines are not durable enough.

## CLI shape

```text
anonsync discovery receipt list --seat self
anonsync discovery receipt show <receipt>
anonsync discovery receipt explain <receipt>
```

## Non-clone reason

Current official Resilio docs still leave discovery dependency change spread across warning pages, troubleshooting notes, and preferences prose.
AnonSync should instead preserve one receipt that later operators can trust without reconstructing the story.
