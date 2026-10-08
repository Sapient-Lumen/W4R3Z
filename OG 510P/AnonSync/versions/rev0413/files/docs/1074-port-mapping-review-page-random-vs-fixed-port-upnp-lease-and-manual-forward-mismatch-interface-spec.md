# Port-mapping review page, random-vs-fixed port, UPnP lease, and manual-forward mismatch interface spec

## Purpose

The ingress contract sheet publishes the posture.
This page decides whether the planned posture is coherent enough to proceed.

The practical review question is:

> does this listener choice, forwarding plan, and continuity expectation actually fit together, or are we combining random ports, router automation, and manual instructions into a brittle story that will mislead the operator?

Current official Resilio docs still expose all the raw ingredients:

- the listening port may be random or manually set
- manual forwarding must target that listening port
- automatic mapping sends UPnP and NAT-PMP packets to a router
- directness can still fail for reasons beyond local intent

AnonSync should make the review first-class rather than scattering the answer.

## When this page appears

Render this review when any of the following is true:

- the user switches from random to fixed listener
- the user leaves the listener random while asking for manual forwarding guidance
- the user enables automatic port mapping
- the user disables automatic mapping on a runtime that previously depended on it
- a known-host, firewall, or support recipe names a specific port
- reachability claims are being upgraded from `relay acceptable` toward `direct preferred`

## Review sections

### 1) Listener continuity fit

Show:

- current listener posture
- target listener posture
- whether operator instructions, peer instructions, or stored repair notes depend on a stable port
- whether the change invalidates existing guidance

Verdicts:

- `stable-and-coherent`
- `stable-but-new`
- `random-and-fragile`
- `mismatch-with-manual-forwarding`
- `unknown`

### 2) Mapping method fit

Show:

- chosen method (`automatic`, `manual`, `none`, `mixed`)
- whether the runtime is allowed to emit router-mutation requests
- whether the operator still must perform manual steps
- whether the combined plan is likely to produce ambiguous blame on failure

Verdicts:

- `automatic-only`
- `manual-only`
- `mixed-with-clear-ownership`
- `mixed-and-ambiguous`
- `none`

### 3) Lease stability fit

Show:

- whether a stable external lease is required for the intended guidance
- whether the product only has attempted mapping or also a visible lease
- whether lease survival is vulnerable to router restart, local port change, or rule replacement
- whether the plan depends on stronger proof than the product has

Verdicts:

- `lease-not-required`
- `attempt-sufficient-for-now`
- `lease-needed-but-unproven`
- `lease-visible-but-brittle`
- `unknown`

### 4) Directness fit

Show:

- whether the operator is asking for `possible directness` or `demonstrated directness`
- whether both sides still need compatible firewalls / routing / remote posture
- whether relay remains part of the expected envelope

Verdicts:

- `directness-not-claimed`
- `directness-possible`
- `directness-demonstrated`
- `relay-still-likely`
- `claim-too-strong`

### 5) Review decision

Return one of:

- `proceed`
- `proceed-with-warning`
- `hold-for-port-pin`
- `hold-for-proof`
- `block`

## Main surface

A compact result should read like one of these:

- `fixed port + automatic mapping is coherent; reachability proof still weaker than directness`
- `random port conflicts with manual forwarding plan; pin port first`
- `mapping attempt allowed, but audience widening accepted only with warning`
- `manual and automatic plans overlap; ownership ambiguous until one is chosen`
- `claim blocked because requested directness is stronger than present proof`

## Required copy blocks

### Strong approval

`Listener continuity is stable enough for the chosen ingress method. Router mutation may still fail, and directness remains a separate proof class.`

### Hold for proof

`This plan requests a stronger reachability sentence than current evidence supports. Keep the port plan if desired, but do not claim outside reachability or direct connectivity yet.`

### Block

`This plan mixes an unstable listener contract with external forwarding expectations. Pin the listener or drop the forwarding claim before proceeding.`

## Event language

Use phrases such as:

- `port continuity reviewed`
- `manual-forward mismatch found`
- `router-mutation plan accepted with warning`
- `directness claim held below proof ceiling`

Avoid phrases such as:

- `network fixed`
- `outside access ready`
- `UPnP solved it`

## Design tests

The page fails if any of these remain true:

- a random listener can still coexist silently with manual-forwarding instructions
- the interface still says `mapping enabled` without judging whether that is enough for the requested claim
- the operator cannot tell whether failure blame belongs to listener continuity, router mutation, or remote-side constraints
