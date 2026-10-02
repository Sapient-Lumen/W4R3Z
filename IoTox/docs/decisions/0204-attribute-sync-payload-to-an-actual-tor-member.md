# ADR 0204: Attribute sync payload to an actual-Tor member

Status: accepted, implemented, and first bounded live sample qualified, 2026-08-27.

## Context

ADR 0203 proves two independently keyed Tor auxiliaries become private-v2 ready in the same
topology that converges a signed tree. Fixed sync scheduling selected the lowest stable route key,
which was the native member in that reusable identity set. Route readiness plus convergence does
not establish that the tree objects crossed Tor.

Adding a general remote route-forcing control would expand product policy for a qualification need.
The existing fixed scheduler and immutable reusable identities already provide a narrower seam.

## Decision

Add distinct scenario `sync-tree-route-private-actual-tor-payload`. For the founding reusable client
identity set, require lane 1's exact public key to sort before lane 2, assign lane 1 to strict Tor in
both guests, and retain fixed scheduling. Fail before workload start if that ordering changes.

After convergence, the client must bind its exact sync job to all of the following:

- `carrier=auxiliary` and `state=complete`;
- `carrier-route` equal to its exact Tor member key;
- the carrier-key SHA-256 equal to the already retained private-route auxiliary commitment; and
- zero auxiliary reassignment.

Normal ADR 0203 Tor STREAM/CIRC, process, configuration, packet-containment, route-readiness, signed
tree, and compact-export conditions remain mandatory. The device receipt names the same Tor member
but only the subscriber's completed job is payload-attribution evidence.

The first clean rerun exposed a separate harness boundary: a transient local `sync-pull` rejection
ended the guest before a job identifier existed, even though both route receipts and the signed
publication were ready. Initial pull admission is idempotent, so the harness now retries it for at
most 120 seconds. It records the exact attempt and failure counts plus a content-free SHA-256 of the
first diagnostic. A successful proof must satisfy `attempts = failures + 1`; a retry is evidence,
not erased history. Exhausting the window still fails the guest and includes the same commitments in
the failure receipt.

## Consequences

- A passing sample proves the complete signed tree pull stayed assigned to the actual-Tor member.
- This is a reusable-identity qualification seam, not a production preference or arbitrary force
  control. Fresh identities may sort differently and must fail rather than silently select native.
- A complete job-to-carrier binding plus zero reassignment attributes IoTox transfer semantics; it
  does not measure Tor goodput, reveal circuit contents, or prove anonymity.
- Transient control admission is visible separately from payload routing. A retry cannot be
  misreported as a first-attempt success and cannot convert a missing completed Tor job into a pass.
- Actual Tor process loss, route withdrawal, reassignment/retry policy, multiple public nodes,
  multiple exits, and duration remain later gates.

## Qualification

Accepted compact proof `pair.lzsyitvy` runs clean commit `38aa432`, completes the signed
4,194,389-byte tree on the exact Tor member commitment
`0a1530b0f9486da2d6dd96855c92357b30d38594a52a4ecfcc889b0e0b2f606c`, and records zero
reassignment. Initial pull admission was one attempt with zero failures. Both roles bind two
successful exact-target streams to distinct three-hop `CONFLUX_LINKED` circuits; their TAP captures
contain 2,469/4,341 Tor-proxy packets and zero unexpected context packets. The strict compact verifier
accepts the same relations. See `../evidence/2026-08-27-sandwurm-actual-tor-payload.md`.
