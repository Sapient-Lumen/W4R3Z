# Connectivity repair page — tracker, LAN, predefined host, and listener ladder interface spec

## Purpose

The archive already had broad recovery objects and route-policy doctrine.
What it still lacked was one ordinary reviewed page for the more practical question:

> these peers are not connecting or are stuck on a weaker path; what is the least-widening repair ladder, and what exactly does each rung change?

Current official Resilio docs make the gap concrete.
They still say failure may come from blocked tracker access, blocked listening ports, blocked relay, proxy involvement, blocked multicast on LAN, and lack of predefined hosts in constrained networks; they also still suggest predefined hosts, port mapping, relay allowance, and LAN multicast as distinct remedies.
That is useful truth.
It should not remain buried in troubleshooting bullets.

## Core decision

AnonSync must expose one first-class **Connectivity repair** page whenever a subject or peer pair is unreachable, repeatedly relayed against policy, or failing to regain a stronger path.

The page exists to answer five things in one place:

1. what the current blocker family actually is
2. what evidence supports that diagnosis
3. what repair rung is narrowest and safest
4. what disclosure or route widening each rung would introduce
5. what receipt will prove the outcome

## Fixed page order

1. **Failure or downgrade verdict**
2. **Evidence basis**
3. **Least-widening repair ladder**
4. **Widening and non-effects**
5. **Receipt promise**

### 1) Failure or downgrade verdict

Show:

- `connectivity_repair_page_id`
- reviewed subject / pair
- current outcome (`unreachable`, `relay-only`, `flapping`, `stale-route`, `unknown`)
- primary blocker class
- strongest honest summary

The operator must be able to answer:

> what category of problem is this before I start widening anything?

### 2) Evidence basis

Show:

- last successful discovery lane
- last successful direct attempt
- whether relay fallback is possible and whether it is currently blocked
- whether listener reachability, multicast, tracker, proxy, or protocol overlap evidence is missing or negative
- whether the problem is local, remote, pairwise, or environment-wide

This section should answer:

> what proof makes this ladder honest rather than speculative?

### 3) Least-widening repair ladder

Render ordered rungs such as:

1. repair existing listener / NAT / firewall truth
2. verify or refresh known host
3. restore LAN multicast on the relevant segment
4. enable tracker discovery
5. enable relay fallback
6. widen broader public-direct posture

Each rung must say:

- exact change
- disclosure delta
- expected route delta
- whether restart, cache clear, or remote matching change is required

### 4) Widening and non-effects

For every rung, show:

- new observers or audiences created
- what it still will **not** fix
- whether remembered endpoint residue survives after success
- what rollback or cache-clear work still remains if posture should be narrowed afterward

This section should keep `repair` from masquerading as `complete diagnosis`.

### 5) Receipt promise

Show:

- the receipt family that will be emitted
- what later audit can prove about blocker class, chosen rung, widening delta, and observed result
- whether the result remains provisional pending remote-side matching or later direct-path verification

## Public object

### Connectivity repair page

Fields:

- `connectivity_repair_page_id`
- `subject_ref`
- `peer_pair_ref` nullable
- `outcome_class`
- `primary_blocker_class`
- `evidence_rows[]`
- `repair_rungs[]`
- `widening_rows[]`
- `non_effect_rows[]`
- `receipt_promise`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. subject / pair
2. outcome class
3. primary blocker
4. next rung
5. widening delta

Example:

```text
Laptop ↔ Vault     unreachable     tracker blocked     Verify known host     no new public observer
```

## Non-goals

This page does **not** replace pairwise route proof or subject-wide disclosure review.
It exists to keep the **repair ladder** honest, narrow, and auditable.

