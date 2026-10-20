# Sandwurm synchronization unclean-restart evidence — 2026-08-21

## Claim

Two concurrent source-linked IoTox NixOS guests under Sandwurm recovered one identical 8 MiB
immutable `range-v1` file revision after an unclean receiver-daemon restart over each supported
native carrier: direct UDP and forced TCP. The forced-TCP guests disabled UDP, local discovery, DHT
announcements, and hole punching and used only the controlled TCP relay.

Each cell rate-shaped the client TAP, began the ordinary two-object pull, and required positive
authoritative c-toxcore receive position before sending `SIGKILL` to the client IoTox daemon. The
content-free crash checkpoint recorded exit status 137, exactly two private transport temporaries,
one signed active-attempt journal, and no accepted HEAD or activation pointer. The guest and
publisher remained alive. Startup recovery retained the same stable device and Tox identities,
removed the exact journal-scoped transport residue, left the staging directory empty, and burned old
attempt IDs rather than reviving lost Tox handles. A fresh exact-revision pull then verified and
committed both immutable objects, accepted the signed HEAD last, and separately activated its exact
record token.

Both carriers converged the same content identities:

```text
artifact bytes          8388608
artifact SHA-256         628137e2ec82540d278434e5214ec1f96765183ad6b8666d4a61fe1a91e2cea5
manifest bytes           786496
manifest SHA-256         4808af6e0e0fc52d19060299854af2a0937bc8b56532471df5b4b854f1ae9fd1
signed HEAD record       e47ab54d788d82b86e5b6ea4ab5c47732c9b3f0a6a15bb8138a252671dd4b62c
generation               1
direct-UDP interrupted   67179 transport bytes
forced-TCP interrupted   71292 transport bytes
```

This accepts unclean receiver-process restart and whole-object retry for M5B. It does not prove
byte-range resume, a guest/kernel restart during transfer, live disconnect/pause recovery,
deterministic directory publication, range reconstruction from a basis, cancellation, multiple
sources, full-disk or read-only recovery, rollback/fork injection, unattended OTA execution, two
physical hosts, or production readiness.

## Defect found and repaired

The first scientific run exposed a real boundary mismatch. `FileTransferManager` receives through a
private `.part.part-XXXXXX` temporary and renames it to the canonical attempt path only at completion.
The signed attempt journal knew the canonical path but recovery did not yet know the transport
temporary, so an unclean stop could fence the attempt while leaking partial bytes and quota.

ADR 0129 binds the exact temporary prefix to the signed attempt ID. Recovery validates one exact
owner-private, singly linked regular-file candidate, removes and directory-fsyncs it before clearing
the journal, and fails closed on malformed, multiple, or linked candidates. The accepted cells ran
only after this repair; the discovery runs are not retained as positive evidence.

## Accepted observations

Both cells used source commit `9e70654590840970ee01668390f18e61a98e2353`, IoTox
`0.39.0 rev0039`, c-toxcore `0.2.23` with the `iotox-file-rr1` scheduler, libsodium `1.0.22`, Argon2
`20190702`, and the same source-linked product binary:

```text
cefbf344ad3cc3830c672820a831e410a68013986e6bb19099b464c971ccd7b3
```

The independently reverified compact exports are:

```text
direct UDP  .sandwurm/exports/pairs/pair.xf1soga1  98304 allocated bytes
forced TCP  .sandwurm/exports/pairs/pair.mxahczbv  98304 allocated bytes
```

Digest bindings:

```text
direct-UDP source manifest  05bc887aa7df62203a1104f02c5939051714917fe10020952c9caf450174abb5
direct-UDP client receipt   d517470e65c6a16dabeb1c8e278d813e3044d00f6897b71fd00f36ffb5918ee3
direct-UDP device receipt   dfff1850a2cb686d971bd36c8d131844624c99e9cd78b95201d013d85534849c
direct-UDP client chain     c4e895365c0880997e6313c198cb724f7f6dd7259499550203fe3fa76c7c6a32
direct-UDP device chain     442ee6707c5cbad15e742fc667fdaf12e6d269c3bf2793fcb1c043ef5a6bfd99

forced-TCP source manifest  492a8bbfc500a1e2ea7f04ef3bbcf719efdb0b058216f977e6e2301df4b24eb8
forced-TCP client receipt   c152ada735e4a0c0f1279434eb02b4a8c5e16431708b0bf892eff177ece6b43c
forced-TCP device receipt   3e0ae4092eaca70f68f2f7bd40b3bd2db99aa8477b483557d8afd879dea3b029
forced-TCP client chain     b637ceccf5d46e44f7752857226d8568b20a48e835b8f60f44504cda54b2d5e9
forced-TCP device chain     62fe342c5c37a3a0ff08cdd455f0936a25c5eefc5959d428df4c4a2b8271a84a
```

Reverification:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.xf1soga1 sync-file-restart
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.mxahczbv sync-file-restart
```

## Secret boundary

The original ignored proof roots contain writable guest disks, copied reusable test identities,
authority and synchronization state, the fixed test-only RecallRoot fixture, and the temporary
bootstrap key. The compact exporter copied only the verifier-consumed JSON allowlist, bound every
file plus the private source manifest digest, declared the omitted secret classes, and reverified
each result. The compact receipts retain only boolean restart classifications, bounded counters,
digests, and transport byte positions—not private staging names, content, phrases, or keys.
