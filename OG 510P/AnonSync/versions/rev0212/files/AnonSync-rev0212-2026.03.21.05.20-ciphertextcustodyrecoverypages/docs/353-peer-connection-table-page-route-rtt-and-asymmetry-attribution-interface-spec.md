# Peer connection table page: route, RTT, and asymmetry attribution interface spec

## Purpose

The archive already had route evidence in principle.
What it still lacked was one fixed page for the ordinary question:

> which peer/path is actually limiting this subject right now, and what proof supports that claim?

Current Resilio docs expose a table with upload/download rate, RTT, and protocol.
AnonSync should keep that strength but make the causality contract stricter.

## Core decision

A peer table is not merely a roster of active connections.
It is a reviewed **causal attribution page**.
Each row should answer whether that peer is:

- a current source
- a current sink
- only present but not limiting
- likely the bottleneck
- exonerated by current evidence

## Fixed review order

1. **Pair identity and scope**
2. **Winning path**
3. **Flow asymmetry**
4. **Limiting-peer verdict**
5. **Counterfactual improvement ladder**

## 1) Pair identity and scope

Show:

- remote peer identity / seat identity
- subject or subtree scope
- whether the row is aggregated or one concrete connection
- freshness of the evidence

The operator must be able to answer:

> what exact pair is this row about?

## 2) Winning path

Show explicitly:

- route class (`direct LAN`, `direct WAN`, `relay`, `proxy-mediated`, `predefined-host pinned`, etc.)
- transport/protocol in force
- whether this is the preferred route or a fallback
- what better route class is theoretically available

Never force the operator to infer `relay` or `better direct route exists` from folklore.

## 3) Flow asymmetry

The page must expose:

- current upload rate
- current download rate
- RTT / latency trend
- whether the remote peer is upload-bound
- whether the local peer is receive/write-bound
- whether asymmetry is expected or suspicious

A slow receiver should not automatically blame its own download side when the source peer is the smaller pipe.

## 4) Limiting-peer verdict

Each row should carry one verdict field such as:

- `not limiting`
- `partially limiting`
- `dominant current limiter`
- `route penalty dominant`
- `disk/finalize penalty dominant`
- `insufficient evidence`

Also show:

- supporting counters
- competing explanations
- what additional evidence would overturn the verdict

## 5) Counterfactual improvement ladder

Provide ordered next actions, for example:

- improve direct reachability
- prefer predefined hosts or same-LAN path
- reduce relay dependence
- wait for a faster source peer to come online
- relieve local disk pressure
- change workload shape rather than network knobs

## Dense rendering obligations

A compact peer row may compress prose, but it must still surface:

- route class
- RTT band
- upload/download asymmetry
- bottleneck verdict
- one-tap path to the full attribution page

## Anti-clone rule

Do not clone peer tables that stop at `rate / RTT / protocol` as bare facts.
AnonSync should treat those fields as evidence for a public verdict, not as the verdict itself.
