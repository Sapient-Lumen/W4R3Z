# ADR 0243: Repeat actual-Tor Ratox churn in a later operator window

Status: accepted bounded repetition; independently witnessed UTC and exit-operator review remain
open, 2026-08-29.

## Context

M8 retains seven strict actual-Tor compact proofs from 2026-08-27/28, including two long-running
Ratox circuit-churn cells and one adversarial local boundary. ADR 0210 accounts their target paths
but deliberately records no qualified time-window separation or independent exit operators. A later
run can test the frozen behavior against a third public Tox record and a new Tor path population. It
cannot manufacture trusted time or operator independence from filesystem timestamps.

## Decision

Repeat `ratox-route-actual-tor-soak` unchanged in the 2026-08-29 operator window against the current
numeric Tox record `144.217.167.73:33445`. Preserve all ADR 0207 requirements: two independent Tor
processes and control sockets, two source-linked Sandwurm guests, 120 paired terminal/heartbeat
samples, exact client/device circuit closes at ordinals 20/100, post-close PING and explicit-resume
branches, stable PTY/session/incarnation identities where required, TCP-only TAP capture, zero
Tor/IoTox/guest process restarts, raw verification, secret-free export, and compact replay.

Add the accepted proof to the deterministic ADR 0210 population report. Continue to report
`time_window_count=0`, `time_window_separation_evidenced=false`, and
`independent_exit_diversity_qualified=false`: this repository records when the operator ran the
cell, but the frozen pair schema has no independently witnessed wall-clock field or exit-operator
mapping.

## Qualification

Accepted compact proof `pair.wbsef5tp` runs product binary SHA-256
`a7eb9e0bc478125a2ced8f9f8c4bd89759364c12689948d594113ebc5fc3ab53` through Tor 0.4.8.11. Both
exact target streams reopen onto distinct three-hop paths after requested circuit closes. The client
close recovers in 12.267 seconds while Ratox remains at epoch 2/generation 1. The device close
recovers in 27.999 seconds, c-toxcore declares authoritative loss, and Ratox explicitly resumes at
epoch 3/generation 2. Input/output positions cross ordinals 21 and 101 exactly.

All 120 samples finish in 353.783 seconds of active probe time. Maximum terminal and heartbeat round
trips are 2.992 and 4.896 seconds. The client/device TAPs contain 2,546/3,118 IPv4 egress packets,
all TCP to their exact role-local Tor listener, with zero native UDP, direct bootstrap, direct relay,
or direct peer packets. The raw proof manifest SHA-256 is
`aef6d7971d34181883a00697ed2e45e48c032de9b18082660bffea6c188a5c77`; the compact manifest and
compact-export digests are `0eb735f0b69c2f59253a96e7446267043c400906c3a88208e5677e75c461c8e3`
and `214a2a562642f83a5acf5b9b65131ccfc1793eb5366c27b544811925badf6dc0`. The compact proof allocates
3,325,952 bytes and independently passes the strict verifier.

The expanded eight-proof report resolves 30 declarations into 24 distinct paths, 20 first hops, 23
last hops, and 24 first/last pairs. This proof contributes four paths, three first hops, four last
hops, and zero path/first-hop/last-hop reuse against each of the seven preceding proofs. The report
SHA-256 is `3986dc9c0d4246afb8876269009cad9e3d136a70e289af54f0ec8bc2abf1f7da`.

## Consequences

- The long-running two-IoTox Tor behavior repeats against a third relay record in a later operator
  window with a wholly new observed path/last-hop population.
- The result again proves that a Tor `stream-reopened` label predicts neither attachment continuity
  nor authoritative loss: the same proof exercises both application outcomes.
- M8 stays open for a schema-bound independently witnessed time campaign and reviewed exit/operator
  populations. No anonymity, unlinkability, availability, latency SLO, or independent operator
  claim is added.

See `docs/evidence/2026-08-29-sandwurm-actual-tor-ratox-repetition.md`.

