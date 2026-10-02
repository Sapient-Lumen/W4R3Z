# ADR 0267: Qualify multi-lane content restart

Status: accepted, 2026-08-31

## Context

ADR 0248 made `CTA1` the signed restart truth for each active content-v2 page or chunk receive.
ADR 0262 later allowed several immutable-object lanes to overlap, and ADR 0266 identified caps two
and four as the useful explicit construction settings. None of those decisions proved what an
unclean client-daemon restart does while several genuine c-toxcore receives are live.

The first live restart experiments exposed a boundary below `CTA1`. The file-transfer manager writes
an admitted receive through a private `mkstemp` file before renaming it to the canonical
attempt-scoped staging pathname. A `SIGKILL` can therefore leave files of the exact form

```text
ROOT/staging/content-v2/objects/HH/.iotox-REST.REQUEST_ID.part.part-XXXXXX
```

while signed recovery correctly sees no canonical partial at
`HH/REST.REQUEST_ID.part`. Those transport files are neither verified CAS objects nor signed
resumable prefixes. Leaving them indefinitely would make restart cleanup incomplete; treating them
as canonical would invent trust that `CTA1` does not grant.

The first forced-TCP retry also found an authority-order race in the laboratory. A restarted client
could verify the publisher and issue a fresh HEAD request before the publisher had consumed the
client's reciprocal authority proof. The publisher correctly denied that request. A restart proof
must therefore establish two-sided recovered authority before releasing the fresh pull; local
readiness at only the requester is insufficient.

## Decision

Extend content-attempt recovery under the namespace transaction with exact transport-temporary
cleanup. Recovery first loads and, when present, verifies the signed `CTA1` journal. It then:

- accepts only the canonical lowercase digest shard and filename grammar above;
- requires private owner-owned mode-0700 staging directories on the namespace device;
- requires each candidate to be a mode-0600 owner-owned single-link regular file on that device,
  with a canonical nonzero decimal request ID, six base-62 `mkstemp` bytes, and size within the
  namespace staging quota;
- refuses any malformed or unsafe staging entry instead of guessing;
- unlinks only exact transport-owned temporaries and fsyncs every changed shard; and
- continues the existing `CTA1` classification only after that cleanup succeeds.

Verified complete CAS objects remain the only reusable byte truth. Canonical exact-size attempt
files still enter CAS only through ADR 0247's verified commit. Strict canonical partials are fenced
and removed. Transport temporaries are never resumed, and recovery itself never accepts a HEAD or
activates a revision.

Add `sync-content-restart-cap-2` and `sync-content-restart-cap-4` to the two-guest Sandwurm matrix.
Each cell uses the same deterministic high-entropy 8 MiB, 24-chunk, one-page, 26-object revision and
an exact signed cap. The root remains serial. Before fault injection the subscriber must expose the
exact number of live admitted non-root lanes, distinct request IDs and FileIds, one source, at least
two exact transport temporaries, positive transport bytes, a signed journal, no accepted HEAD, and
no activation. The host sends `SIGKILL` only to the subscriber IoTox process.

On startup the complete CAS inventory must be byte-for-byte and digest-for-digest identical to its
crash inventory, with zero newly committed objects. Exact transport temporaries and canonical
partials must both be zero. The publisher and subscriber independently report the recovered
authorized session before the host releases a distinct explicit pull. Only that different job may
converge and activate.

Keep content-v2, `CTA1`, FileId, local-control, and Ratox framing unchanged. Keep the process default
at one. This decision qualifies the already-explicit caps two and four; it does not introduce an
automatic profile.

## Findings

All four final-tree cells pass strict raw replay, compact export, and strict compact replay with
IoTox binary SHA-256
`531dfb224e133b3fc0735455f1a5d077c02dbf6a6c2a91b0e0d85f766321d5b6`.

| Proof | Carrier | Cap/live lanes | Crash transport files/bytes | Preserved CAS | Fresh job |
| --- | --- | ---: | ---: | ---: | --- |
| `pair.8j7v2irm` | direct UDP | 2/2 | 2 / 219,360 | 2 objects / 1,328 bytes | distinct |
| `pair.9q9hsx40` | direct UDP | 4/4 | 4 / 356,460 | 2 objects / 1,328 bytes | distinct |
| `pair.8ulddb9t` | forced TCP | 2/2 | 2 / 204,279 | 2 objects / 1,328 bytes | distinct |
| `pair.ol5goyug` | forced TCP | 4/4 | 4 / 311,217 | 2 objects / 1,328 bytes | distinct |

Every recovered CAS inventory has the exact crash digest
`a77184f53e12f91e9790d5e16ec84ca5147bcae1c8f6f8cadceba17d1ae08a07`, zero object
delta, zero post-start transport files, and zero canonical partials. Every first job differs from
its replacement. Every cell accepts HEAD last and activates only after complete convergence.

See `../evidence/2026-08-31-sandwurm-sync-content-restart.md`.

## Consequences

The roadmap's multi-lane client-daemon restart gate is closed for explicit caps two and four on
native direct UDP and forced TCP. IoTox now distinguishes all three restart byte classes:

1. verified complete CAS objects are durable reusable truth;
2. exact canonical `CTA1` staging receives are verified, committed, or fenced by signed recovery;
3. exact c-toxcore transport temporaries are private implementation residue and are removed.

The rejected forced-TCP attempt strengthens the authority contract: a locally ready requester is
not evidence that the peer has authorized it. The two-sided laboratory barrier records that fact
without adding a peer acknowledgment or changing protocol framing.

This ADR does not qualify content partial-prefix resume, transparent same-job continuation, whole-VM
or power-cut recovery, arbitrary filesystem faults, hostile same-owner mutation, I2P/Tor content
restart, physical-host diversity, same-source auxiliary-path distribution, or a persistent-Ratox
cap-two SLA. Those remain separate gates.
