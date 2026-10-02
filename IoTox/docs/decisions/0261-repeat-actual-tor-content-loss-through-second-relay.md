# ADR 0261: Repeat actual-Tor content loss through a second relay

Status: accepted, 2026-08-30

## Context

ADR 0260 qualified fail-closed loss of one selected actual-Tor content worker, but its accepted
proof used one public Tox TCP-relay record in one operator window. The safety mechanism was therefore
independently verified, while relay-record diversity for this exact content-v2 fault remained open.
The wider M8 gate also asks for exit, time-window, adversarial-boundary, and long-running topology
coverage; one repetition cannot close those dimensions.

The pair runner derives a host manifest from two completed guest receipts. Its multi-source loss
fields had accumulated copied scenario allowlists. The second run exposed one missed copy:
`multi_source_loss_head_fenced_role_count` remained zero even though both immutable guest receipts
recorded the required true value. The independent verifier correctly rejected that manifest.

## Decision

Repeat the unchanged `sync-content-multi-route-actual-tor-loss` gate against a second public Tox
TCP-relay record compiled into the pinned provider:

```text
205.185.115.131:443
3091C6BEB2A993F1C6300C16549FABA67098FF3D62C6D253828B531470B53D68
```

Keep ADR 0260's acceptance contract unchanged: positive complementary-source progress, whole-job
failure, clean staging, no accepted HEAD or activation, zero reassignment or downgrade, recovery of
the same signed route under a new worker incarnation, unchanged native authority epochs, and
convergence only through a distinct explicit pull.

Derive every common multi-source-loss manifest field from one
`CONTENT_MULTI_SOURCE_LOSS_SCENARIOS` set. Freeze its two members in the runner self-test. For this
completed run, rebuild only the omitted host-derived head-fenced role count from the two unchanged
guest receipts, then require the existing strict verifier to accept both the raw root and compact
export. Do not change a guest receipt, checkpoint, capture, protocol frame, or product binary.

## Evidence

Accepted compact proof `pair.i8ar90tx` records:

- target `205.185.115.131:443` with the exact public key above;
- stopped worker `17305418366285522271` at 76,776 bytes and recovered worker
  `9399449097838626368` on the same signed route;
- failed job `5356260296355692902` and distinct replacement job `2192547647293893774`;
- two committed immutable objects and 528 fetched bytes before failure;
- one carrier loss, zero reassignment, one recovery, and unchanged native epochs `1/1`;
- five primary-source and two secondary-source objects in the successful replacement pull;
- two Tor 0.4.8.11 instances at 100% bootstrap, two independently observed three-hop application
  circuits, and five client plus three device successful guest-source streams;
- client/device TAP proxy counts `3,768/5,025` and zero unexpected-context packets; and
- the same source-linked binary SHA-256
  `efc0b415f4198a67949ab7fce70b5c30f83c6cff3c6b69d4262b46ba9674fa04` in both receipts.

The independent verifier accepts the raw proof and its 15,286,272-byte compact export. The compact
pair-manifest SHA-256 is
`7a5e235ca2ead66d4052186d4f9f5f7fa3499ac687bab4f5754315f8163bb932`; the compact-export record
SHA-256 is `fa68af587bf1eb6e63c889ed769a1e85c7eb18e3c3d4945fbebb37af456dd7f4`. See
`../evidence/2026-08-30-sandwurm-sync-content-actual-tor-loss-second-relay.md`.

## Consequences

The exact content-worker-loss mechanism now has accepted repetitions through two distinct public
Tox relay records. The second relay produced the same authority and fail-closed outcome with
different job, worker, circuit, stream, and capture identities. This is useful evidence against a
single-relay accident and makes the host manifest aggregation less prone to scenario drift.

This does not close the M8 population checkbox or Gate 5. Both samples are same-computer, two-VM,
bounded runs on the same date and Tor build. The compact evidence observes circuit fingerprints but
does not independently review exit operators or prove physical-path independence. It also does not
establish hours-long churn, randomized fault distributions, cold startup with an absent route,
independent bottlenecks, anonymity, availability, same-source striping, or a performance gain.
