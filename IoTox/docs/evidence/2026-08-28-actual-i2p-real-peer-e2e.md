# Actual-I2P real-peer E2E evidence — 2026-08-28

## Claim

Two fresh source-linked IoTox peers completed the existing genuine real-peer lifecycle through two
distinct i2pd 2.60.0 processes and three persistent I2P Tox-service fronts on the founding host.
This is actual-I2P, actual-c-toxcore, exact-application evidence. It is not a two-machine, anonymity,
independent-operator, Sandwurm packet-containment, or production-route claim.

## Frozen provider and topology

```text
IoTox 0.45.0 rev0045
c-toxcore 0.2.23+iotox-file-rr1-tcp-connect120
libsodium 1.0.22, linked static
client i2pd SAM: 127.0.0.1:47656
server i2pd SAM: 127.0.0.1:37656
IoTox SOCKS boundary: 127.0.0.1:39056
```

Three exact public Tox node endpoints were each mapped, without address translation, to a distinct
persistent I2P Destination. The service side forwarded to an exact numeric-loopback port, and a
bounded raw TCP shim reached only that record's public relay. Destination commitments retained in
the content-free adapter audits were:

```text
205.185.115.131:53      d04cd340eae05c8a730beff3ac0fe874c8bfe3125a6200d41fe7d10808050d47
139.162.110.188:33445   85b810479fe7a26864179a4451f34a1936236c51ae0d1109f1dbd574bc99c59b
3.0.24.15:33445         ed7f512b7492802d2a800a7fdb942b6295df4dd16ab630b2ebd07c5a77b92a80
```

The node records were selected from a point-in-time public Tox status snapshot while all three
reported UDP and TCP healthy. They are evidence inputs, not IoTox defaults or endorsed
infrastructure.

## Falsification ladder

1. One unconnected local `DHT_bootstrap` plus one fake logical endpoint completed I2P and encrypted
   relay handshakes but stayed offline.
2. Seeding that local relay into one public DHT node still did not produce a useful path population.
3. One healthy public relay through direct strict SOCKS stayed offline for a fresh TCP-only client.
4. Three healthy public relays through direct strict SOCKS reached `tcp` in under ten seconds.
5. Three I2P fronts addressed as `192.0.2.x` completed all relay handshakes but returned no onion
   replies, because Tox embedded those aliases in the remote path.
6. The same three fronts keyed by their real numeric node addresses reached `tcp` in about twenty
   seconds.
7. Repeating step 6 with the TCP-establishment-only provider also reached `tcp`; this falsified the
   proposed onion-retention patch, which was removed.

## Complete application result

`tools/run-real-peer-smoke.sh --fresh-keys` passed with the three plural bootstrap/relay inputs. Its
content-free terminal summary was:

```text
real-peer-smoke=pass
key-mode=fresh
key-lifecycle=fresh-generated-disposable
session=canonical-hello-transcript-confirmed-both-directions
authority=stable-principal-proof-and-read-telemetry-grant-both-directions
owner-reentry=denied-device-then-recalled-owner-proof
self-delegation=owner-role-denied-applied-exact-duplicate
remote-revocation=applied-exact-duplicate-and-inactive-after-restart
delegation-restart=revoked-controller-recalled-and-redelegated-at-sequence-4
ownership-epoch=successor-nominated-transitioned-exact-duplicate-replayed-at-epoch-2
phrase-compromise-cut=old-owner-denied-successor-reentered-and-redelegated
transport-mode=tox/i2p-construction
message=delivered-to-peer-journal
command=device.describe-received-succeeded-and-durably-reloaded
summary=system.summary-received-succeeded-and-typed
file=finite-exact-bytes-completed
friendship=removed-both-directions-and-readded-with-fresh-session-proof
reconnect=process-restart-fresh-session-and-authority-proof
restart-identity=tox-and-stable-device-preserved
```

The two 39-byte finite-file fixtures compared byte-identically. After the carrier was already ready,
the final TCP-only-provider repetition measured 137 ms initial peer convergence and 57 ms reconnect
convergence; those values must not be misreported as I2P route-start latency. Both peers retained
35 open descriptors. The final resident sets were 9,976 and 9,796 KiB; the earlier
experimental-provider pass measured 9,456 and 9,932 KiB.

## Remaining gate

Production `tox/i2p` remains unsupported. The remaining M8 edge is a two-guest Sandwurm cell that
binds exact packet containment, adapter/router loss and recovery, private route-member proof, and
one Ratox or sync payload into raw plus compact secret-free verification.
