# Route provenance sheet page: discovery source, listener, and current path witness interface spec

## Purpose

After any serious reachability diagnosis or policy change, operators need one durable answer to:

> how are these peers actually finding each other right now, which listener or helper made the path possible, and what evidence supports that story?

## Core decision

Every serious subject/peer pair and every serious cohort route view must expose one first-class **Route provenance sheet**.

The sheet owns:

- counterpart scope
- discovery source
- transfer path class
- listener / ingress basis
- helper dependence
- path witness freshness
- better-route counterfactual

## Fixed page order

1. counterpart pair header
2. discovery-source ledger
3. transfer-path ledger
4. listener and ingress basis
5. counterfactual route card

### 1) Counterpart pair header

Show:

- local seat / subject
- remote counterpart or cohort slice
- current path class (`direct lan`, `direct wan`, `relayed`, `proxy-constrained`, `predefined-host bootstrapped`, `unknown`)
- strongest safe sentence

### 2) Discovery-source ledger

Render discovery evidence rows with:

- discovery source (`LAN broadcast`, `tracker`, `predefined host`, `manual seed`, `cached address`, `unknown`)
- source plane
- currently active? (`yes`, `historical`, `fallback`, `unknown`)
- freshness
- proof artifact

### 3) Transfer-path ledger

Render transfer-path rows with:

- path class
- helper dependence
- directness grade
- witness time
- route bottleneck if known

### 4) Listener and ingress basis

This section is mandatory.
Show:

- effective listening port / bind basis if relevant
- whether the current path needs public ingress
- whether UPnP / manual forwarding / predefined host knowledge made the route possible
- whether multi-interface ambiguity or proxy posture narrows confidence

### 5) Counterfactual route card

Show:

- better route available? (`yes`, `no`, `unknown`)
- what would have to change to remove helper dependence
- what would fail if the current helper disappeared
- whether the path is robust, fallback-only, or brittle

## Rules

### Rule 1 — provenance includes history and now

Discovery may be historical while transfer path is current.
The sheet must preserve both without collapsing them.

### Rule 2 — helper dependence is not shameful but must be visible

Relay, proxy, tracker, and predefined-host dependence must be described plainly.

### Rule 3 — witness freshness must be ordinary

A route claim without freshness is incomplete.

## Acceptance criteria

A later operator can:

- tell how the counterpart was discovered
- tell what route is being used now
- tell which helper or ingress basis makes it possible
- tell whether the path is direct, relayed, or proxy-constrained
- tell what counterfactual would break or improve the route
