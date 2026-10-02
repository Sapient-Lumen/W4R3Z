# ADR 0208: Repeat Ratox churn across a distinct relay record

Status: accepted bounded relay-record repetition, 2026-08-28.

## Context

ADR 0207 accepts one continuous-process actual-Tor Ratox circuit-churn proof. M8 asks for broader
relay, exit, and time sampling, but those dimensions must not be collapsed into one vague
"diversity" claim. A second public Tox record can test whether the frozen gate repeats without
changing its contract and can challenge any accidental inference from Tor stream transitions to
Ratox session transitions. It cannot establish independent Tor exits or a separated time window.

## Decision

Repeat `ratox-route-actual-tor-soak` unchanged against a distinct, contemporaneously reviewed,
operator-supplied numeric TCP record. Require the same 120 samples, exact client/device circuit
closes, authenticated before/after inventories, raw requested-close ordering, process continuity,
session/incarnation/PTY/byte invariants, post-churn PING/explicit-resume branch, TAP containment,
source-linked guests, raw verification, secret-free export, and compact verification as ADR 0207.

Compare Tor `stream-reattached`/`stream-reopened` labels with the independently observed Ratox
outcome, but grant neither Tor label authority to declare attachment continuity or loss. Record the
second endpoint and proof separately; do not aggregate it into an availability percentage or an
exit-diversity claim.

## Qualification

Accepted compact proof `pair.9cx0jels` runs clean commit
`e33b4bd72aee912f0ad8d94640e0ea473912ae18` and the same IoTox binary SHA-256 as ADR 0207 through
record `3.0.24.15:33445`. Both exact streams reopened on distinct qualifying three-hop circuits in
17.273 and 17.174 seconds. Nevertheless, both post-churn PINGs returned at online epoch 2,
generation 1; no attachment resumed. All 120 samples, exact byte positions, unchanged Tor/IoTox/VM
processes, and 5,890 TCP-only guest-egress packets pass the strict raw and compact verifier. The raw
proof allocates 2,547,585,024 bytes and the secret-free compact proof allocates 3,297,280 bytes.

Together with `pair.k8o54n2v`, the retained evidence covers two distinct public Tox relay records,
four deliberate circuit closes, both Tor transition labels, and both Ratox lifecycle outcomes. In
particular, a reopened Tor stream appears with both application continuity and explicit resume.
Tor transition type therefore is evidence, not session authority.

## Consequences

- The claim advances from one relay record to two sequential relay-record samples on one host and
  date. It does not advance to exit diversity, independent time-window diversity, availability,
  anonymity, or an SLA.
- The post-churn two-branch protocol remains frozen. No optimization may map `stream-reopened`
  directly to detach/resume or map `stream-reattached` directly to continuity.
- The next bounded cells are an adversarial local-proxy gate and repetitions separated by operator-
  selected time windows with explicit relay and Tor-path-population accounting.
