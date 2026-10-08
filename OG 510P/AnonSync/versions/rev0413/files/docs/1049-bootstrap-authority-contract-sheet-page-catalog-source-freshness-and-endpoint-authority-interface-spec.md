# Bootstrap authority contract sheet page, catalog source, freshness, and endpoint-authority interface spec

## Purpose

The archive already had route policy, helper infrastructure, and basic connectivity explanation language.
What it still lacked was one explicit contract for the narrow but critical question:

> who currently tells this seat where peer-discovery and fallback infrastructure exist, and how trustworthy and fresh is that answer?

Current official Resilio docs make the missing contract unusually obvious.
They still say tracker and relay addresses are learned from `sync.conf`, that connectivity failure can begin with inability to reach that file, and that later route behavior separately depends on tracker, relay, LAN discovery, listening ports, and predefined hosts.

That is not just troubleshooting detail.
It is endpoint-authority state.

AnonSync should therefore render one first-class contract sheet for bootstrap authority before the operator is asked to reason about route failure or discovery health.

## Core decision

Every seat must expose one explicit **bootstrap authority contract**.
It must say:

- what source currently defines endpoint infrastructure
- what endpoint classes that source may define
- whether that source is policy-chosen, default, inherited, cached, or absent
- whether the current answer is fresh, stale, expired, or validation-failed
- what stronger sentence the product must refuse

The product must never let `tracker enabled`, `relay enabled`, or `healthy` stand in for bootstrap authority truth.

## Fixed review order

Every bootstrap-authority contract sheet should render the same sections in the same order:

1. **Authority source**
2. **Endpoint classes governed**
3. **Freshness and trust posture**
4. **Fallback if this authority disappears**
5. **Strongest safe sentence**

### 1) Authority source

This section should show:

- source class (`public-catalog`, `private-catalog`, `manual-static`, `cached-bootstrap-state`, `none`)
- source locator
- how the source was selected (`default`, `policy`, `manual pin`, `legacy carry-forward`)
- which seat or policy approved it

The operator must be able to answer: **who currently defines infrastructure for this seat?**

### 2) Endpoint classes governed

This section should show:

- tracker endpoints
- relay endpoints
- rendezvous/directory endpoints if present
- whether LAN discovery sits outside this authority
- whether manual hosts override or supplement this authority

The operator must be able to answer: **what parts of route discovery actually depend on this source?**

### 3) Freshness and trust posture

This section should show:

- last success time
- last failed refresh time
- validation posture (`trusted`, `stale-trusted`, `expired`, `signature-failed`, `parse-failed`, `transport-failed`, `unknown`)
- whether the seat is actively using fresh data, stale cached data, or no authority data

The operator must be able to answer: **is the source reachable, valid, and current enough to trust?**

### 4) Fallback if this authority disappears

This section should show one honest envelope such as:

- `manual hosts remain`
- `LAN discovery remains`
- `cached endpoints remain until aged out`
- `existing direct peers may persist; new public discovery blocked`
- `no fallback envelope remains`

The operator must be able to answer: **what would still work if this source vanished right now?**

### 5) Strongest safe sentence

The page must end with one sentence such as:

- `public bootstrap authority is healthy and fresh`
- `bootstrap authority is stale; cached endpoints may still permit limited continuity`
- `no bootstrap authority is present; discovery depends on manual/LAN-only paths`
- `bootstrap validation failed; endpoint authority not trusted`

And it must also show the stronger blocked sentence it refuses, such as:

- `all peer discovery is healthy`
- `new peers can still join normally`
- `connectivity is broken`

## Public objects

### `bootstrap_authority_contract`

Fields:

- `bootstrap_authority_contract_id`
- `seat_ref`
- `source_class`
- `source_locator`
- `selection_basis`
- `governed_endpoint_classes[]`
- `validation_posture`
- `freshness_state`
- `last_success_at` nullable
- `last_failure_at` nullable
- `fallback_envelope_summary`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `generated_at`

## Main surface

A compact row should read like one of these, not just `tracker on`:

- `public bootstrap authority · fresh`
- `private bootstrap authority · pinned by policy`
- `bootstrap stale · cached endpoints only`
- `no bootstrap authority · manual/LAN discovery only`
- `bootstrap untrusted · validation failed`

## Event language

Use phrases such as:

- `bootstrap authority refreshed successfully`
- `bootstrap authority stale; cached endpoint residue retained`
- `manual infrastructure pin replaced public catalog`
- `bootstrap authority absent by policy`

Avoid phrases such as:

- `tracker enabled`
- `relay available`
- `connectivity should work`

Those lines are too narrow or too optimistic.

## CLI shape

```text
anonsync discovery authority show --seat self
anonsync discovery authority explain --seat self
anonsync discovery authority pin --source private-catalog
anonsync discovery authority refresh --seat self
```

## Design tests

The model is not explicit enough if any of these remain true:

- the operator can see tracker or relay toggles without seeing the authority source that defined them
- stale cached endpoints can remain in use without the contract sheet saying so
- LAN discovery and manual hosts are not visibly separated from catalog-governed infrastructure
- the product can still say `healthy` without owning freshness and trust posture

## Non-clone reason

Current official Resilio docs still make bootstrap authority feel like a background implementation detail of `sync.conf` and later troubleshooting.
AnonSync should instead render endpoint authority, freshness, and fallback as an ordinary first-class contract.
