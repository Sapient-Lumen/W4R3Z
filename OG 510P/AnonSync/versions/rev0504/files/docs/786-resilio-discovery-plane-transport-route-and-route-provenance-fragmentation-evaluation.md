# Resilio discovery plane, transport route, and route-provenance fragmentation evaluation

## Purpose

The archive already had topology slicing, capacity isolation, representative-pair review, and diagnostic route doctrine.
What it still lacked was one explicit comparison document for another ordinary operator question:

> when the operator asks `are we direct, relayed, tracker-dependent, LAN-discovered, or predefined-host-driven right now — and did that route match the intended policy over the incident window?`, where does the product itself own the answer?

Current official Resilio docs are good enough that AnonSync needs a serious answer.
Resilio is not vague about the ingredients.
It documents tracker discovery, relay fallback, LAN multicast, predefined hosts, listening-port reachability, relay icons in the peer list, protocol rows in the performance table, and folder-level helper toggles.
That candor is worth preserving.

## What Resilio gets right

Resilio is still right that:

- discovery policy and transport route are not the same thing
- direct versus relayed connection materially changes speed expectations
- tracker, LAN search, predefined hosts, and relay each play distinct roles
- peer rows and relay icons are useful current-state witnesses
- multi-NIC routing mistakes, blocked ports, or blocked helper services can change the effective route

This is much better than products that hide all transport posture behind one optimistic `connected` label.

## What still should not be cloned

The route-truth contract is still scattered and too support-shaped.
Current official Resilio docs still require the operator to combine at least five article families:

1. **What ports and protocols are used by Sync?** for the ordered model of config-file fetch, tracker discovery, direct TCP/UDP attempts, relay fallback, and LAN multicast
2. **What is a Relay Server?** for the current explanation of relay necessity, relay penalty, and the relay icon shown in peer list
3. **Folder Preferences** for per-folder helper posture such as relay enabled, tracker enabled, LAN search, and predefined hosts on all peers
4. **Performance Overview** for the live protocol row in the connection table
5. **Peers aren't connecting / slow-speed troubleshooting** for practical causes like blocked tracker, blocked relay, blocked listening port, multiple NICs, relay slowdown, and direct-port mapping advice

That means one ordinary answer is still reconstructed from several places:

- what discovery helpers were intended for this folder?
- what transport route was actually observed for this peer pair?
- whether the current route matched policy or fell back because of failure
- whether the route changed during the incident window or only at the instant the operator looked
- what exact sentence is safe about route provenance right now

The substance is useful.
The workflow ownership is still weak.

## Why this matters for AnonSync

AnonSync should not repeat two common mistakes:

1. **policy/route collapse** — treating `relay allowed`, `tracker enabled`, or `predefined hosts configured` as if they already prove the effective route
2. **single-glance overclaim** — treating one current peer icon or protocol row as if it fully explains the incident window

A serious sync product needs one stable public answer to four different questions:

- **route-intent truth** — what discovery and fallback posture was desired for this subject?
- **effective-route truth** — what route class was actually observed for the measured pair or cohort?
- **provenance truth** — over what window, from which witnesses, do we believe that route statement?
- **divergence truth** — did the route differ from policy, and what is the cheapest honest corrective rung?

## Replacement pages in this revision

This revision adds four fixed pages:

- `787` — Route posture
- `788` — Route evidence
- `789` — Route divergence review
- `790` — Route provenance receipt

Together they make intended helper posture, observed route class, evidence window, policy mismatch, and claim ceiling explicit before AnonSync lets `direct`, `relay`, or `tracker problem` become durable incident language.

## Concrete product stance

Borrow from Resilio:

- candid separation of tracker, LAN, predefined-host, direct, and relay concepts
- candid visibility for relay icons and current protocol rows
- candid admission that blocked helpers and multi-NIC routing can change the effective path
- candid acknowledgment that relay is a fallback with performance consequences

Do not clone from Resilio:

- leaving route truth split across current icon, current protocol row, helper toggles, and troubleshooting prose
- letting folder preferences imply effective route without a provenance window
- making the operator infer whether a route statement covers one glance, one run, or the whole incident
- letting route mismatch advice exist without one reviewed desired-vs-observed object

## Evaluation summary

Resilio still deserves credit for not pretending that connectivity is one boolean.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `what route did this incident actually take, how do we know, and did that match policy over the relevant window?`

AnonSync should therefore make **route provenance** a first-class product object.
Every serious connectivity or speed investigation should publish desired helper posture, observed route class, evidence window, route-switch history, mismatch verdict, strongest safe sentence, and forbidden stronger sentence before the product treats `direct` or `relay` as coherent incident truth.
