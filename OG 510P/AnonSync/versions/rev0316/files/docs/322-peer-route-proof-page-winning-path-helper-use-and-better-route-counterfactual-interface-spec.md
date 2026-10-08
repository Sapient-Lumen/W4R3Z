# Peer route proof page: winning path, helper use, and better-route counterfactual interface spec

## Purpose

This page answers one ordinary question:

> for this peer pair on this subject right now, what path actually won, why did it win, and what exact change would produce the cleaner route I expected?

The page exists because `relay`, `direct`, `LAN`, `known host`, and `connected` are not sufficient explanations.

## Core decision

Every serious peer detail and transfer lane must be able to open one first-class **Peer route proof** page.
That page owns:

- current winning route
- directness grade
- helper use now versus merely allowed
- the losing route candidates and blockers
- a counterfactual planner for better routes

The workbench must not force the operator to infer path truth from icons, vague status strings, or support lore.

## Primary layout

The page always renders the same regions in the same order:

1. pair strip
2. current route card
3. route-candidate ladder
4. blocker matrix
5. counterfactual planner
6. route receipts

### 1) Pair strip

Show:

- subject label
- local seat
- remote seat or peer cluster
- current route verdict: `lan-direct`, `known-host direct`, `public-direct`, `relay-assisted`, `relay-inevitable`, `blocked`, `unknown`
- one next honest action

### 2) Current route card

This card publishes:

- winning route class
- whether the route is symmetric or asymmetric
- directness grade
- helper use now
- confidence and freshness of the verdict

The operator must be able to answer: **what path is really carrying bytes right now?**

### 3) Route-candidate ladder

This card publishes candidate paths in rank order:

- LAN direct
- manually pinned direct
- public direct
- relay
- blocked/no viable path

Each row shows:

- whether the candidate was attempted
- why it lost or won
- which side blocked it
- whether retry is automatically pending or requires review

The operator must be able to answer: **why did the better-looking path lose?**

### 4) Blocker matrix

Rows may include:

- blocked inbound listener
- bootstrap catalog unreachable
- tracker unreachable or disabled
- relay unreachable or disabled
- proxy asymmetry
- stale endpoint residue
- multiple-NIC confusion
- multicast/subnet boundary issue
- address-family mismatch

The operator must be able to answer: **what typed condition is preventing the route I wanted?**

### 5) Counterfactual planner

This card publishes reviewed statements such as:

- `If local direct ingress were proved, this pair would likely switch from relay-assisted to public-direct.`
- `If both peers added the same manual endpoint pins, tracker dependence would drop but directness would still depend on ingress proof.`
- `If LAN discovery were re-enabled on both seats in the same subnet, the pair would likely become lan-direct.`
- `If proxy posture remains unchanged on both sides, relay remains inevitable.`

The operator must be able to answer: **what exact change is worth trying next?**

### 6) Route receipts

Receipts show:

- route changes
- helper-policy changes affecting the pair
- blocker acknowledgments
- exported path explanations

## Non-negotiable rules

### Rule 1 — current route and ideal route must be separate rows

The product may not imply that the current path is the preferred one merely because it works.

### Rule 2 — helper use must be typed

`relay in use` is not enough.
The page must say whether relay is optional, situational, or inevitable.

### Rule 3 — pairwise explanation must survive after the route changes

A later direct route must not erase the receipt explaining why the pair was relayed earlier.

## Honest outputs

The page may conclude:

- `Current route is relay-assisted; public-direct candidate lost because remote ingress remains unproved.`
- `Current route is lan-direct; tracker and relay are allowed but not carrying this pair.`
- `Current route is blocked; bootstrap catalog access failed before discovery could begin.`
- `Current route is known-host direct; manual pin is carrying the pair because tracker is disabled by policy.`

It may not collapse those outcomes into one generic `connected` or `not connected` chip.
