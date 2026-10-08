# Ingress exposure contract sheet page, listening port, map authority, and lease truth interface spec

## Purpose

The archive already had reachability, discovery, and audience pages.
What it still lacked was one explicit contract for the narrower router-facing question:

> if this runtime asks to become easier to reach from outside its local host, what exactly is local listener intent, what mutation authority is being used, and what proof do we actually have?

Current official Resilio docs make the missing contract unusually obvious.
They still say the listening port carries core traffic, that the value may be random unless pinned, that manual forwarding depends on that port, and that enabling UPnP port mapping sends packets to the router.
That is not just a convenience toggle.
It is ingress posture.

AnonSync should therefore render one first-class **ingress exposure contract sheet** before the operator is allowed to treat `better direct connectivity` as a small preference.

## Core decision

Every seat capable of widening inbound reachability must expose one explicit **ingress exposure contract**.
It must say:

- which local listener is being requested
- which authority plane would try to make it reachable
- what audience widening is only attempted versus proven
- what side effects or adjacent-device risks are in play
- what stronger sentence the product must refuse

The product must never let `Use UPnP`, `open direct connection`, or `fix slow sync` stand in for this truth.

## Fixed review order

Every ingress exposure contract sheet should render the same sections in the same order:

1. **Local listener contract**
2. **Ingress mutation authority**
3. **Requested audience**
4. **Proof ceiling**
5. **Strongest safe sentence**

### 1) Local listener contract

This section should show:

- listener port posture (`fixed`, `random`, `inherited`, `config-owned`, `unknown`)
- transport families that depend on it
- whether the port is continuity-bearing for manual forwarding, known hosts, firewall rules, or operator instructions
- whether changing it would invalidate existing ingress assumptions

The operator must be able to answer: **what local port truth is this flow anchored to?**

### 2) Ingress mutation authority

This section should show:

- mutation mode (`none`, `automatic-upnp`, `automatic-nat-pmp`, `manual-forward-expected`, `mixed`, `unknown`)
- mutation authority holder (`local-operator`, `router-automation`, `external-admin`, `unknown`)
- whether the product will emit packets or requests beyond the host boundary
- rollback posture (`instant`, `next-router-refresh`, `manual-only`, `unknown`)

The operator must be able to answer: **what infrastructure outside this host is being asked to change, by whom, and how reversibly?**

### 3) Requested audience

This section should show:

- audience class (`host-local`, `lan-peers`, `upstream-nat-reachable`, `internet-routable-candidate`, `unknown`)
- whether the audience widening is newly requested or already lived
- whether other control surfaces or listeners are widened separately
- whether the requested audience is merely inferred from mapping attempt rather than proven

The operator must be able to answer: **who is newly in the candidate inbound audience if this succeeds?**

### 4) Proof ceiling

This section should show:

- proof class (`listener-only`, `mapping-attempted`, `lease-visible`, `reachable-from-outside`, `direct-peer-proven`, `relay-only`, `unknown`)
- invalidators such as random-port change, router restart, firewall mismatch, multiple-NIC ambiguity, or remote-side blockage
- whether the proof is current, stale, or absent
- the exact stronger claim still blocked

The operator must be able to answer: **what is the strongest honest connectivity sentence right now?**

### 5) Strongest safe sentence

The page must end with one sentence such as:

- `fixed listener chosen; router mapping request would be emitted`
- `mapping attempted; external reachability still unproven`
- `lease visible; direct peer connectivity still not demonstrated`
- `manual forwarding expected; current port is continuity-bearing`
- `ingress widening refused because side-effect or audience risk was not accepted`

And it must also show the stronger blocked sentence it refuses, such as:

- `the port is open to the internet`
- `direct connection is guaranteed`
- `this is just a local speed preference`
- `turning this off fully retracts every prior mapping immediately`

## Public objects

### `ingress_exposure_contract`

Fields:

- `ingress_exposure_contract_id`
- `seat_ref`
- `runtime_namespace_ref`
- `listener_port_posture`
- `listener_port_value`
- `transport_scope[]`
- `mutation_mode`
- `mutation_authority_holder`
- `requested_audience_class`
- `proof_class`
- `proof_observed_at`
- `proof_invalidators[]`
- `rollback_posture`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `generated_at`

## Main surface

A compact row should read like one of these, not just `UPnP enabled`:

- `fixed listener 32459 · automatic router-mapping request · directness unproven`
- `random listener · no stable forwarding contract`
- `manual forwarding expected · port continuity now matters`
- `lease visible · remote direct proof still missing`
- `router-side mutation refused pending review`

## Event language

Use phrases such as:

- `ingress exposure contract prepared`
- `router mapping authority requested`
- `listener continuity changed`
- `directness claim withheld`
- `audience widening accepted`

Avoid phrases such as:

- `faster sync enabled`
- `network optimization on`
- `open port succeeded`
- `connectivity fixed`

Those lines are too strong and too flattening.

## CLI shape

```text
anonsync ingress contract show --seat self
anonsync ingress explain --runtime ns_01J...
anonsync ingress proof show --seat self
```

## Design tests

The model is not explicit enough if any of these remain true:

- the operator can request automatic mapping without seeing that infrastructure outside the host may change
- random-vs-fixed port continuity still looks irrelevant when forwarding guidance depends on it
- mapping attempt and direct-proof still collapse into one green success state
- the interface can still say `UPnP enabled` without saying who might now be able to knock on the listener

## Non-clone reason

Current official Resilio docs still preserve the important distinctions, but they do so across preferences, config comments, troubleshooting, and speed tips.
AnonSync should instead render local listener truth, mutation authority, requested audience, and proof ceiling as one stable reviewed object.
