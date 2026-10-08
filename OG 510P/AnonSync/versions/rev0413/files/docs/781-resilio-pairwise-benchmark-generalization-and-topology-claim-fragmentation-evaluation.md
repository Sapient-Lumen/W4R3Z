# Resilio pairwise benchmark generalization, topology-claim fragmentation, and representative-pair absence evaluation

## Purpose

The archive already had performance visibility, pairwise bottleneck attribution, throughput expectation, witness-set doctrine, and capacity-isolation experiments.
What it still lacked was one explicit comparison document for another ordinary seam:

> when the operator says `does this one measured peer pair really explain the incident for the rest of the mesh?`, where does the product itself own the representativeness test, the counterexample search, and the ceiling on any wider claim?

Current official Resilio docs are good enough that AnonSync needs a serious answer.
Resilio is not unserious about topology.
It exposes per-peer connection rows, admits asymmetric uploader effects, says more high-upload peers can raise download speed, treats predefined hosts and helper settings as per-folder and per-peer realities, and still escalates stubborn speed cases to logs from all peers.
That honesty is worth preserving.

## What Resilio gets right

Resilio is still right that:

- performance truth can differ by peer pair, not just by share
- one slow uploader can drag down other peers
- more strong uploaders can change the observed download ceiling
- pairwise network benchmarking is sometimes useful
- persistent speed incidents may require evidence from all peers, not only the currently visible pair

This is better than products that flatten a swarm into one optimistic bandwidth number.

## What still should not be cloned

The generalization contract is still scattered and too support-shaped.
Current official Resilio docs still require the operator to combine at least five article families:

1. **Performance Overview** for a table of current peer connections with upload, download, RTT, and protocol
2. **Slow-speed troubleshooting** for the claims that one slow uploader can depress others and that more fast uploaders can raise the effective download rate
3. **Speed-improvement guidance** for topology-changing advice such as direct paths, VPN/LAN shaping, and predefined hosts
4. **Folder Preferences** for the fact that predefined hosts and helper settings are configured per folder and should be used on all peers when replacing tracker/LAN search
5. **iperf3 instructions** for an external benchmark that is explicitly pairwise and requires Sync to be shut down on both peers during the test

That means one ordinary answer is still reconstructed from several places:

- is this measurement about one pair or the whole incident topology?
- which other peers or directions could still falsify the conclusion?
- when is a pair merely illustrative rather than representative?
- when does the product need a wider topology slice before suggesting a tuning or route change?
- what exact sentence is still safe about the whole mesh after a single-pair measurement?

The substance is useful.
The workflow ownership is still weak.

## Why this matters for AnonSync

AnonSync should not repeat two common mistakes:

1. **representative-pair folklore** — letting one benchmarked or visible pair masquerade as a share-wide verdict
2. **mesh-wide overclaim** — turning `this pair is slow for this reason` into `the system is slow for that reason` without topology coverage review

A serious sync product needs one stable public answer to four different questions:

- **slice truth** — which peers, directions, and workloads are actually covered by the evidence?
- **representativeness truth** — why is this pair believed to stand in for others, if it does at all?
- **counterexample truth** — which seats, directions, or route classes could still falsify the current theory?
- **generalization truth** — what is the strongest safe sentence about the wider incident right now?

## Replacement pages in this revision

This revision adds four fixed pages:

- `782` — Topology slice
- `783` — Representativeness review
- `784` — Topology extrapolation
- `785` — Topology measurement receipt

Together they make pairwise measurement coverage, generalization ceiling, and counterexample search explicit before AnonSync lets one neat benchmark or one peer row speak for the whole mesh.

## Concrete product stance

Borrow from Resilio:

- candid peer-row visibility
- candid asymmetry language
- candid admission that all-peer evidence may still be needed
- candid pairwise benchmarking instructions when network isolation is the actual question

Do not clone from Resilio:

- leaving the operator to infer whether a pairwise result generalizes
- mixing live peer rows, pairwise iperf, and all-peer escalation without one topology coverage object
- making `more fast uploaders would help` and `collect logs from all peers` coexist without saying what present evidence already covers

## Evaluation summary

Resilio still deserves credit for not pretending that speed is one scalar truth.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `which topology slice is covered by this evidence, and how far may I generalize from it?`

AnonSync should therefore make **representative-pair judgment** a first-class product object.
Every serious performance investigation should publish covered peer set, uncovered counterexample set, direction coverage, topology-homogeneity basis, strongest safe generalization, and forbidden stronger sentence before the product treats one pairwise measurement as system truth.
