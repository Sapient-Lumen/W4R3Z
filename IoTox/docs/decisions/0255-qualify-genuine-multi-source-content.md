# ADR 0255: Qualify genuine multi-source content on native UDP

Status: accepted direct-UDP product gate, 2026-08-30; forced-TCP qualification pending.

## Context

ADR 0254 activated exact multi-source consumption in the product receiver and qualified it against
the deterministic provider. The remaining question was whether two independently authorized live
c-toxcore peers, each holding only part of one frozen content fabric, could both contribute to one
subscriber job in source-linked Sandwurm guests.

The first lab fixture made an invalid assumption: four logical chunk positions meant four distinct
physical CAS files. The deterministic 4 MiB artifact actually contains only two distinct 1 MiB chunk
digests. The corrected fixture parses the authenticated paged root and page records, assigns distinct
physical chunk identities between sources, and measures which source supplied every logical chunk
occurrence.

## Decision

Accept genuine multi-source content-v2 over direct UDP. Two source identities and one subscriber run
as three IoTox agents in two simultaneous KVM guests. Each source independently satisfies v3
authority and namespace writer policy. The original source alone supplies the frozen signed HEAD;
the added source can supply only exact immutable objects. Both sources must answer exact sparse
availability and contribute object traffic before whole-artifact reconstruction, HEAD-last
acceptance, and explicit activation can pass.

Do not extend that claim to forced TCP. The forced-TCP harness remains available and fail-closed.
Thirteen bounded 900-second variants established that relay capacity, request ordering, and
reusable-key admission are not individually sufficient to keep a second forced-TCP source
application-ready for one subscriber Tox identity in this c-toxcore topology:

- one relay let the primary friendship confirm but not the secondary;
- registering two independent fixtures as both bootstrap nodes and relays prevented the primary
  friendship from confirming;
- keeping the client in bootstrap domain A and the secondary in domain B restored the primary but
  not the secondary; and
- one common bootstrap domain with publisher-specific relays A and B produced the intended four
  stable TCP sessions and confirmed the primary, but the secondary session still did not confirm.
- serializing the secondary friend request until after primary confirmation in that same
  publisher-specific topology produced five stable relay sessions, but the secondary still did not
  confirm; and
- attaching all three identities to both independently keyed relays while retaining serialized
  friendship admission produced six stable relay sessions and primary confirmation, but the
  secondary still did not confirm.
- a diagnostic repeat proved the secondary stayed Tox-offline with `connected=0`, no carrier, and
  zero IoTox HELLO attempts despite the same six relay sockets;
- the ordinary one-request/explicit-accept ceremony never exposed the primary pending request in
  the isolated fixture, proving that local relay sockets are not an onion request-delivery network;
- mutual known-key `transport-peer-accept` made the primary deterministic in both full-mesh and
  publisher-specific layouts, but the secondary remained offline with zero HELLO attempts; and
- a hybrid reusable-key construction let the device pre-accept while the client supplied the full
  Tox address. With common bootstrap A plus publisher relays A/B, the secondary briefly passed the
  exact TCP/confirmed checkpoint, then fell offline for the complete 300-second authority window.
  Confining the secondary bootstrap and relay to B removed the extra socket but also removed that
  transient success.

These are topology-specific observations, not a claim that c-toxcore universally supports only one
TCP friend or that adding relays can never help. A future forced-TCP gate must change the friendship
or route-identity construction and pass the existing exact content assertions. It must not widen the
deadline again or reinterpret relay sockets as authenticated Tox sessions.

## Qualification

Accepted compact proof `pair.u80_yp7r` binds one 4,194,304-byte paged revision, four logical chunks,
one page, two sources, four availability requests/results, and positive object traffic from both
sources. Deduplication yields three logical chunk occurrences from the primary and one from the
secondary. The device reports five primary object requests and one secondary object request. Both
roles agree on the artifact, root manifest, signed HEAD, authority, convergence, activation, and
terminal truth. The secret-free compact proof independently passes strict replay.

Rejected forced-TCP observations are `pair.w5xdce8a`, `pair.yq63hq4o`, `pair.5_ns69s9`,
`pair.65pchyu1`, `pair.kz_b8aqu`, `pair.e246dutm`, `pair.krdg001v`, `pair.vps8gh0q`,
`pair.wkaoqike`, `pair.cmvi_god`, `pair.5c2o3ake`, `pair.tc5w6e8k`, and `pair.cznfp0_q`. They
support only the failure-boundary analysis above and are not accepted proof roots. The retained
harness is the strongest hybrid: subscriber on A+B, primary publisher on A, secondary publisher
with bootstrap A and relay B, primary-before-secondary admission, device pre-accept, and client
full-address request. Content-free failure receipts preserve secondary session/carrier and HELLO
state. Host relay sockets are never interpreted as protocol confirmation.

## Consequences

- Genuine multi-source is now a product claim for native direct UDP, not merely a deterministic
  mock-provider result.
- Logical availability and physical CAS inventory remain distinct because content deduplication can
  map several logical positions to one physical digest.
- Multiple live TCP relay sockets are transport observations, never substitutes for confirmed
  friendship, principal proof, source authority, or object receipts.
- Forced-TCP multi-source convergence, selected-source loss, daemon restart, multiple content lanes,
  comparative performance, physical-host diversity, and hostile network behavior remain open.
