# ADR 0207: Qualify Ratox duration across actual-Tor circuit churn

Status: accepted bounded route qualification, 2026-08-28.

## Context

ADR 0206 proves explicit Ratox recovery after one complete client Tor process loss. That is a hard
outage boundary, but it does not show what an attached interactive session feels like over time or
whether ordinary Tor circuit replacement is mistaken for session mutation. M8 still needs duration
and circuit-churn evidence before broader relay, exit, time, and adversarial-proxy matrices are useful.

Ratox session truth, Tox carrier truth, the route heartbeat, and Tor circuit identity are separate
layers. Tor control evidence itself cannot advance a Tox online epoch, detach a PTY, reset terminal
byte sequences, or declare application progress. A live circuit close may nevertheless break the
SOCKS/TCP stream and cause c-toxcore to report authoritative offline; only that provider truth may
drive the already-frozen detach/explicit-resume lifecycle.

## Decision

Add the opt-in Sandwurm scenario `ratox-route-actual-tor-soak`. Both primary agents run through
independent real Tor processes under the strict topology frozen by ADRs 0190, 0191, and 0195. One
Ratox echo attachment performs 120 heartbeat, PTY, and render samples at a one-second inter-sample
interval. The host pauses the probe after samples 20 and 100 and sends one authenticated, bounded
`CLOSECIRCUIT` command to the exact application circuit used by the client and device respectively.

Acceptance requires:

1. one terminal session and host-incarnation commitment across all 120 samples, with contiguous
   input and output byte sequences and a paired successful heartbeat before every PTY exchange;
2. one raw `REASON=REQUESTED` circuit close at each checkpoint, with authenticated before/after
   `stream-status` and `circuit-status` snapshots proving that the attributed guest stream either
   reopened under a new stream ID or reattached under the same stream ID on a distinct
   three-or-more-hop application circuit;
3. unchanged Tor PID and control-socket inode for the affected role and zero Tor/IoTox daemon
   restarts;
4. an immediate post-replacement PING resolves each checkpoint into exactly one truthful branch:
   canonical PONG with unchanged online epoch/generation, or exact `unavailable` followed only by
   explicit resume under a higher authenticated epoch and generation increment; either branch keeps
   session/incarnation and next byte positions exact;
5. at least 119 seconds between the first and last controller sample; and
6. strict TAP containment: each guest may emit only TCP to its exact role-local Tor SOCKS endpoint,
   with zero native UDP, direct bootstrap, direct relay, or direct peer packets.

The proof retains only commitments for Tor stream IDs, circuit IDs, and circuit paths, plus the
content-free authenticated inventory snapshots. The strict verifier reparses the raw control events
and snapshots to join each commitment to its exact source, target, success, built circuit, requested
close, and replacement order.

## Consequences

- Circuit churn adds no automatic route migration or new protocol framing. It may remain transparent
  at the Ratox attachment when a post-replacement PONG crosses the same epoch, or it may break the
  provider carrier and require the frozen explicit generation-changing resume lifecycle.
- A pass supports resumable session/PTY/byte continuity through two controlled circuit replacements; it
  is not an anonymity, relay-diversity, exit-diversity, public-network availability, or latency-SLA
  claim.
- Killing Tor remains the ADR 0206 recovery cell. This scenario deliberately keeps Tor and IoTox
  processes alive so ordinary circuit churn is not conflated with process loss.
- The next privacy frontier after acceptance is a repeated relay/exit/time matrix and an adversarial
  local-proxy cell, not another change to Ratox framing.

## Qualification

Accepted compact proof `pair.k8o54n2v` closes this bounded gate. Two simultaneous source-linked
Sandwurm/KVM guests ran clean commit `77a020003c717e886f26b02efea5afe65d3b0fdb` and the identical
IoTox binary while their primary agents used independent Tor 0.4.8.11 processes. One terminal
completed all 120 paced heartbeat/PTTY exchanges in 476.708 seconds of active probe time. The
client checkpoint reattached the same stream to a distinct circuit in 123.813 ms and preserved
online epoch 2/generation 1. The device checkpoint reopened a stream in 30.220 seconds, reached
authoritative loss, and explicitly resumed the same session/incarnation/PTY at epoch 3/generation
2 and exact byte position 101. Both circuit closes report raw `REASON=REQUESTED`; both roles retain
unchanged Tor process and control-socket identities; Tor/IoTox/guest restart counts are zero.

The strict verifier independently accepts both the 2,583,646,208-byte private root and the
3,129,344-byte secret-free compact export. The two TAP captures contain 2,862 and 2,961 IPv4 egress
packets respectively, all TCP to the exact role-local Tor listener and none to a bootstrap, relay,
or peer directly. The retained evidence is documented in
`docs/evidence/2026-08-28-sandwurm-actual-tor-ratox-churn.md`. This promotes only the bounded
one-host/relay/Tor/time claim described above; the diversity and adversarial-proxy frontier remains
open.

ADR 0208 repeats this unchanged gate through a distinct public Tox record as compact proof
`pair.9cx0jels`. Both exact Tor streams reopen while both application checkpoints remain
same-epoch/generation continuous. That comparison reinforces this decision's layer boundary:
`stream-reopened` itself neither declares carrier loss nor authorizes Ratox resume.

The rejection history is retained because it materially shaped the accepted proof. The first live
attempt failed closed before its
first mutation because the host selector mixed historical control-event circuit state with the live
stream inventory and stopped on an irrelevant non-application candidate. The corrected selector
joins event-attributed guest stream IDs to authenticated `GETINFO stream-status` and
`circuit-status`, then selects only a currently successful qualifying application circuit.

The corrected second attempt closed the exact client application circuit while Tor and IoTox stayed
alive. Tor built a replacement stream/circuit, but c-toxcore subsequently reported authoritative
offline and the controller correctly returned terminal error 4: the session may be resumed under a
new authenticated epoch. The run was rejected at sample 20 because its original acceptance contract
incorrectly required a single attachment. This is the protocol result: active Tor circuit closure is
not necessarily transparent to the Tox TCP carrier. The gate must therefore preserve the remote PTY,
session/incarnation, and exact byte positions through the explicit-resume branch.

The third attempt observed the other lawful branch: after exact circuit replacement, the attachment
did not emit `unavailable`. The probe waited for an error without sending application traffic and
timed out, so the run was correctly rejected. Together the second and third attempts falsify any
deterministic assumption that `CLOSECIRCUIT` always is or is not transparent to the Tox TCP carrier.
The final gate sends a canonical post-replacement PING. A PONG must preserve epoch/generation; an
`unavailable` must lead to exact higher-epoch resume. Both branches retain session/PTY/byte truth.

The fourth attempt reached sample 100 after the client checkpoint passed by same-attachment PONG,
then rejected the device checkpoint because the original host contract required both a distinct Tor
stream ID and a distinct circuit ID. The device TAP proves its guest-to-SOCKS TCP connection remained
open until teardown, while Tor's authenticated live inventory moved the attributed stream to a new
circuit. That is Tor stream reattachment, not a missing route. The then-v2 churn envelope therefore
requires a distinct circuit but truthfully records either `stream-reattached` (same stream ID) or
`stream-reopened` (new stream ID); raw event ordering must prove the corresponding transition.

The fifth attempt failed before mutation at sample 14 when c-toxcore reported the peer
authoritatively offline despite both Tor processes remaining alive. The configured
`144.217.167.73:33445` record was absent from the official `nodes.tox.chat` TCP-ready inventory when
reviewed on 2026-08-28. This is rejected baseline/public-relay evidence, not circuit-churn evidence:
the acceptance run must use a currently reviewed numeric TCP relay and must still fail on any
unplanned carrier loss. It also reinforces that one accepted relay sample cannot become a public
relay SLA or production route-set recommendation.

The sixth attempt used a freshly reviewed `205.185.115.131:33445` TCP relay and completed all 120
samples plus both requested circuit replacements. Proof sealing then failed closed because the new
lifecycle serializer referenced an undefined local `initial_generation`; no lifecycle receipt means
no accepted proof even when transport work completed. The serializer now receives immutable initial
generation/input/output snapshots explicitly, and its deterministic self-test constructs and checks
the complete lifecycle envelope before another live run.

The seventh attempt completed and sealed all 120 samples. Both requested circuit closes produced
authoritative Tox loss followed by explicit resume of the same session/incarnation: online epochs
2→3→4 and attachment generations 1→2→3 with exact byte positions 21 and 101. Final role-evidence
collection then failed closed because it chose the first historical successful stream whose original
Tor event still labeled its then-unlinked Conflux circuit, instead of the later successful stream on
a currently `CONFLUX_LINKED` application circuit. The shared selector now scans newest-first and
skips every built circuit whose purpose or hop count is not qualifying; its self-test puts an
irrelevant newer success ahead of a valid application stream. The unmanifested run remains rejected.

The eighth attempt completed both churns and 120 samples, with client explicit resume and device
same-epoch attachment continuity. Final device attribution then exposed Conflux's actual control
semantics: stream 60 first reported `SUCCEEDED` on circuit 23, the requested close moved that same
stream to linked circuit 24 without another `SUCCEEDED` event, and the eventual `CLOSED` event named
circuit 24. Tor's control specification defines every STREAM event circuit ID as the circuit to
which the stream is attached, while circuit purpose can change after `BUILT`. The run remained
rejected because the checkpoint inventories had only in-memory commitments. The v3 envelope now
retains authenticated before/after stream and circuit inventories, verifies their digests and exact
target/path/purpose, accepts a same-stream transition only when the eventual raw close names the
replacement circuit, and lets final role attribution use a later raw `CLOSED` circuit record carrying
the linked Conflux purpose. A distinct replacement circuit remains mandatory.
