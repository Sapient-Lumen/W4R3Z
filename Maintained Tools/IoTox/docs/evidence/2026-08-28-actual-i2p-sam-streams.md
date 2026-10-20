# Actual-I2P SAM stream evidence — 2026-08-28

## Claim

One bounded same-host construction run sent one warm-up and four simultaneous measured streams
through IoTox's strict numeric SOCKS5-to-SAM adapter, two distinct live i2pd processes, and the
public I2P network. Every payload arrived and echoed byte-identically. This proves only the actual
I2P STREAM seam below c-toxcore.

It does not prove Tox-over-I2P, guest packet containment, route loss/recovery, multi-host behavior,
Ratox or sync behavior, anonymity, relay/operator diversity, availability, or production latency.

## Frozen inputs

```text
IoTox source commit   a1f3b53129ee15997a6f7f26be5d71d799aab837
i2pd                  2.60.0 (I2P 0.9.69)
i2pd executable SHA   9d537e84fd9808a40435305b04ca3c05819b8f2cf005808b475777bafe87d500
i2pd source entries   315
i2pd source-tree SHA  f06e0917255e5cd3b772ffe9722e141f8842bf262d448ccc437292e8e4f739f0
receipt SHA-256       264af9436ddb7996d185c37f0bb01d7c911571a1e70428c78224073f3f23e281
```

The two routers used separate temporary data directories, process identities, external router ports,
and numeric-loopback SAM listeners. HTTP proxy, SOCKS proxy, BOB, I2CP, and transit contribution were
off. At capture the server/client processes owned 12/49 committed public TCP peers. The receipt
contains counts and domain-separated sets, not addresses.

## Run

The server created one transient Ed25519 STREAM Destination with unencrypted LeaseSet2,
ECIES-X25519 leaseset keys, and two inbound/two outbound tunnels. The separate client router hosted
the ADR 0211 outgoing-only transient session. A shared domain-separated commitment joins the exact
traditional b32 mapped by the adapter to the server Destination without retaining the raw name.

```text
server session setup        9.017760732 s
warm-up attempts            1
warm-up discovery denials   0
warm-up bytes               4,096
warm-up latency             2.526408703 s
measured client start span  82,150 ns
measured stream count       4
bytes per stream            65,536
total measured bytes        262,144
remote Destination count    1
stream latencies            23.688956779 s
                            24.970003544 s
                            25.390280520 s
                            24.722474229 s
```

All client/server status records are `passed`; the client and server payload sets equal the four
deterministically reconstructed payload hashes. The adapter audit contains one generation-1 ready
record followed by exactly five admissions and no denial or loss. Its canonical JSONL bytes rehash
to the receipt's audit commitment.

## Findings during construction

The first attempt used four pending i2pd `STREAM ACCEPT` sockets. Two passed and two were closed.
Review of the exact 2.60.0 source found both accept-queue expiry loops selecting entries whose
three-second deadline was still in the future. The accepted runner consequently uses one pending
accept while processing established streams concurrently. It does not claim that SAM itself has a
one-accept limit.

A later attempt reached the adapter before the new LeaseSet was discoverable and correctly returned
four `denied-stream` results. The final gate therefore separates a bounded, fully recorded warm-up
from the barrier-released measurement. One subsequent run passed but was rejected because its server
and adapter used different commitment domains for the same b32 name. The accepted commit unifies
those domains so the retained verifier can join them without raw naming material.

## Verification

```sh
python3 tools/verify-i2p-sam-smoke.py \
  artifacts/rev0045/i2p-sam-two-router-smoke.json
```

With the exact Nix inputs still installed:

```sh
python3 tools/verify-i2p-sam-smoke.py \
  artifacts/rev0045/i2p-sam-two-router-smoke.json \
  --router-binary /nix/store/zpzbzak08qdld4cfb9vvk075v7nkvzzh-i2pd-2.60.0/bin/i2pd \
  --router-source /nix/store/aw8cyvm53mndnc9n9dlvvfkhls4vcf7a-source
```

Both commands pass. The second independently rehashes the exact executable and complete source
tree. The verifier also binds the adapter blob at the historical IoTox source commit. It verifies
receipt structure and commitments; it does not recreate ephemeral process/socket observations.

See ADR 0212 and `docs/i2p-route-construction.md` for the boundary and next gate.
