# IoTox authenticated route set v1

V1 is the preserved compatibility format. New mixed-context deployments should author
[`route-set v2`](protocol-route-set-v2.md), which signs the coarse network class without changing
artifact size or peer framing.

**Implemented:** transport-neutral signed inventory and coordinator state machine

**Wire allocation:** none

**Signer:** stable IoTox device identity

**Artifact size:** `156 + 48 * member-count` bytes; 252..924 bytes for 2..16 members

The route set says which independent Tox identities are current roads to one stable IoTox device.
It grants no command, terminal, synchronization, or firmware capability. Those remain in the
authority ledger and must be proved through the confirmed application transcript.

## Fixed header

All integers are unsigned big-endian. Unused bytes are zero.

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 8 | ASCII `IOTOXRS1` |
| 8 | 1 | format version, exactly `1` |
| 9 | 1 | minimum route protocol, exactly `1` in v1 |
| 10 | 2 | zero |
| 12 | 8 | route-set generation, nonzero |
| 20 | 32 | stable device Ed25519 public key |
| 52 | 32 | coordinator Tox public key |
| 84 | 2 | member count, 2..16 |
| 86 | 6 | zero |
| 92 | `48*N` | canonical member records |
| `92+48*N` | 64 | Ed25519 signature |

Each member record is:

| Member offset | Size | Meaning |
|---:|---:|---|
| 0 | 32 | nonzero Tox public key |
| 32 | 1 | role: `1` protected, `2` bulk |
| 33 | 1 | connection class: `1` TCP, `2` UDP, `3` either |
| 34 | 2 | maximum active work, nonzero |
| 36 | 2 | automatic restart budget |
| 38 | 2 | zero |
| 40 | 8 | expiry as Unix milliseconds; zero means no wall-clock expiry |

Members are strictly increasing by Tox public key. Duplicate keys, noncanonical order, unknown enum
values, zero identities, zero work budgets, anything other than exactly one protected route, wrong
length, and nonzero reserved bytes fail closed.

## Signature and verification

The signature message is the printable ASCII domain
`IOTOX-ROUTE-SET-SIGNATURE-V1` immediately followed by the complete header and member body. The
stable device identity named at offset 20 signs that message with Ed25519. A verifier requires its
locally expected stable device principal and an operator-selected minimum acceptable generation;
therefore a correctly signed foreign or older artifact is still rejected.

The current v1 decoder accepts only route protocol floor 1. Later protocol versions must add an
explicit compatibility rule; silently interpreting a higher or lower semantic version as v1 is
forbidden.

## Coordinator admission

A member begins `configured`, then follows:

```text
configured -> connecting -> authenticated -> ready
                                   |           |
                                   +-> recovering <-+
                                          |
                                     unavailable
```

Authentication requires all of the following exact inputs:

- listed member Tox public key;
- one nonzero, uniquely owning local worker ID;
- confirmed IoTox application transcript;
- the signed stable device principal;
- the exact route-set generation;
- a route protocol at or above the signed floor; and
- a connection class allowed by the signed member policy.

Unknown, duplicate, unconfirmed, stale-generation, foreign-principal, downgraded, expired, and
wrong-connection-class routes cannot become authenticated. Work is admitted only in `ready`, never
beyond the signed member budget. Recovery drops admitted capacity immediately, increments the
restart counter before replacement, and becomes permanently `unavailable` when its budget is
exhausted. A replacement worker may claim a member only after the old worker is in `recovering`.
Any nonzero expiry also requires a trusted nonzero wall-clock sample when constructing the
coordinator. Agent startup supplies it only after the persisted command-clock rollback check passes;
unavailable or rolled-back time never turns an expiring membership into a permanent one.
Operator-visible failures are a closed content-free enum (`none`, `connection`, `authentication`,
`policy`, `restart-exhausted`, `worker`, `transport`, or `internal`), never worker-supplied text.

## Durable generation checkpoint

`iotox --identity PATH route-set-create OUTPUT GENERATION COORDINATOR_KEY MEMBER...` is the
implemented offline authoring entrance. It requires two through sixteen members in the exact form
`KEY:protected|bulk:tcp|udp|either:WORK:RESTARTS:EXPIRES_MS`, validates the existing stable identity,
signs and canonically re-verifies route-set-v1, and creates one owner-private output without
replacement. It does not load a daemon, update a running coordinator, generate route savedata, or
advance the local generation checkpoint. Operators review and install the artifact separately.
The command reports `format=1`. It cannot encode a network class; member bytes 38..39 remain zero
and local status renders `network-class=unspecified`.

`--route-set PATH` activates strict pre-network loading. The complete signed artifact is hashed with
domain `iotox-route-set-artifact-v1`. A fixed 152-byte `IOTOXRG1` state record binds version 1, the
highest accepted generation, artifact digest, stable device public key, and a 64-byte device
signature over `IoToxHash("iotox-route-generation-state-v1", first 88 bytes)`.

The policy, checkpoint, and persistent lock are private, owner-owned, single-link regular files;
their immediate parent directories are owner-owned mode 0700.
Loads use `O_NOFOLLOW` and exact bounds under an exclusive advisory lock. A new generation is
checkpointed and strictly reread before acceptance. Lower generations and different artifacts at
the same generation fail closed. This detects ordinary local rollback and forks. ADR 0307 adds the
optional `--witness-route-generation` stronger boundary: explicit device-signed enrollment anchors
the reviewed current generation/digest in the authenticated remote service, and every subsequent
artifact must be exactly one generation newer. A fixed device-signed local intent binds the next
checkpoint around pending/committed external CAS. Complete artifact/checkpoint restoration, gaps,
forks, and unresolved service state then fail before route construction. This claim still requires
the witness service to live outside the Agent's administration/storage/snapshot failure domain.

## Operator projection and retained work

Local control v1.24 operation 66 returns the same coherent snapshot used by `iotox routes` and
`iotox routes-watch`: stable-principal digest, generation, public route key, role, connection class,
lifecycle, worker incarnation, work/restart budgets and counters, expiry, and typed failure. It
contains no private key,
peer content, or arbitrary diagnostic text.

With no route-set policy configured, the existing single-route product remains the only path and the
surface returns `mode=single` plus `route-set-configured=0`. Explicit worker activation constructs
independent exact-key transports. Reciprocal transcript-derived route bindings, exact worker
lifecycle, immutable-object assignment, fenced reassignment, and protected Ratox are implemented
and Sandwurm-qualified for the documented same-context cells.

Route-set v1 is not a private cross-route discovery format. Its auxiliary binding exchange contains
the complete signed member roster. ADR 0198 therefore freezes v1 for the accepted same-context
construction only: a native/Tor inventory must first cross an already authority-authenticated
primary association and auxiliary paths must use the member-scoped v2 proof before mixed-context
operation can satisfy the M8 privacy exit. ADR 0199 allocates and implements that construction
codec: type 26 carries this unchanged signed artifact on the authorized primary, while type 27
carries a fixed proof for one member and the complete artifact digest on the auxiliary transcript.
ADR 0200 implements its Agent orchestration behind a separate explicit gate; no v1 framing is
reinterpreted to imply the new property. ADR 0201 qualifies that v2 property across native and
strict generic-SOCKS worker contexts; it does not make the laboratory forwarder Tor.
