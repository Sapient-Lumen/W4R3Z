# Reachability repair review page: bootstrap, firewall, NAT, proxy, and LAN ladder interface spec

## Purpose

This page answers one ordinary question:

> if peers are blocked, slow, or unexpectedly relayed, what is the safest repair ladder, which host or network layer should I touch first, and what retest would prove success without widening more than necessary?

The page exists because `open ports`, `enable relay`, `add predefined hosts`, and `check firewall` are not one honest repair plan.

## Core decision

Every seat with degraded reachability must be able to open one first-class **Reachability repair review** page.
That page owns:

- failure-family classification
- the least-destructive repair ladder
- widening cost of each candidate action
- the retest witness required after each step
- rollback guidance if the attempt fails

The workbench must not force the operator to bounce between warning rows, support prose, and router folklore.

## Primary layout

The page always renders the same regions in the same order:

1. incident strip
2. failure-family card
3. repair ladder
4. widening-cost card
5. retest and rollback card
6. repair receipts

### 1) Incident strip

Show:

- affected subject or seat
- affected peer or peer class
- current incident verdict: `bootstrap-failure`, `discovery-failure`, `direct-ingress-failure`, `relay-failure`, `lan-discovery-failure`, `proxy-constrained`, `mixed-cause`, `unknown`
- one next honest action

### 2) Failure-family card

This card publishes:

- strongest known failure family
- evidence floor for that classification
- weaker alternative hypotheses still open
- whether the failure is local, remote, or pairwise

The operator must be able to answer: **which layer actually looks broken first?**

### 3) Repair ladder

This card publishes rungs in safe order, for example:

1. confirm bootstrap catalog access
2. confirm tracker policy and reachability
3. confirm listener bind and ingress proof
4. review proxy posture and egress-only constraints
5. review relay reachability if direct remains impossible
6. review LAN multicast/broadcast and subnet assumptions
7. add or repair manual endpoint pins only if simpler rungs fail

Each rung shows:

- likely scope of change
- privacy/reachability widening risk
- expected success witness
- whether rollback is trivial or reviewed

The operator must be able to answer: **what should I try first, and why not something riskier?**

### 4) Widening-cost card

This card publishes:

- exposure cost of each candidate change
- whether the change broadens discovery, relay use, or endpoint publication
- whether the change affects only one seat or all peers
- whether the change is temporary or durable by default

The operator must be able to answer: **what am I paying in exposure or complexity for this repair attempt?**

### 5) Retest and rollback card

This card publishes:

- the minimum retest after each rung
- the stop condition proving success
- the signal proving the rung failed
- the exact rollback or narrowing step if the rung widened posture without solving the issue

The operator must be able to answer: **how will I know this fix really worked, and how do I undo it cleanly if it did not?**

### 6) Repair receipts

Receipts show:

- repair ladders approved
- rung attempts made
- retest results
- rollback actions
- final success or abandonment verdict

## Non-negotiable rules

### Rule 1 — the page must distinguish widening from diagnosis

Testing a wider route is not the same action as proving the previous route was broken.

### Rule 2 — manual pins belong late in the ladder

Pinned endpoints are powerful but should not impersonate first-line diagnosis.

### Rule 3 — success must be witnessed, not hoped

A rung is not complete until the page records the expected retest witness.

## Honest outputs

The page may conclude:

- `First safe rung is bootstrap verification; tracker and direct ingress cannot be judged until catalog access is restored.`
- `Direct ingress failure remains strongest cause; do not widen relay yet because local bind changed recently and ingress proof is stale.`
- `Relay path is the lowest-risk temporary repair for this proxy-constrained pair; directness remains a later repair track.`
- `LAN discovery failure is probably subnet- or multicast-related; adding manual pins would bypass the issue but also obscure whether local discovery is really fixed.`

It may not collapse those outcomes into one generic `network issue` label.
