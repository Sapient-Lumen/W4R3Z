# Operator Tor public-route evidence

Date: 2026-08-27

Status: accepted bounded actual-Tor/public-relay route evidence; not anonymity or two-peer application evidence

## Claim

One source-linked IoTox 0.45.0 rev0045 process from clean source commit
`715e1c823b4dabaf7b7a7a9b967a6a8c4b1420a0` reached authoritative Tox TCP self-connectivity through
an operator-owned Tor 0.4.8.11 daemon and the public numeric Tox TCP relay
`144.217.167.73:33445`, key
`7E5668E0EE09E19F320AD47902419331FFEE147BB3606769CFBE921A2A2FD34C`. The relay record was selected
from the live public registry at `https://nodes.tox.chat/`; it is evidence input, not a new compiled
default.

Tor control authentication independently observed each one-shot configured-target SOCKS stream
from a new IoTox source port through the same stream ID's `NEW` and `SUCCEEDED` events. Both were
attached to built three-hop `CONFLUX_LINKED` application circuits. Tor's Conflux bundles multiple
ordinary exit circuits for application traffic; the gate accepts only `GENERAL` or
`CONFLUX_LINKED`, records the exact purpose, and rejects internal, onion-service, testing, and
controller purposes. Linux process socket ownership simultaneously showed that IoTox
had only a TCP stream to its loopback Tor SOCKS endpoint and no UDP or direct public-relay socket.
The Tor process—not IoTox—owned public TCP connections.

The gate then terminated Tor, waited for c-toxcore's authoritative `offline`, held the route absent
for 30 leak checks, restarted the exact Tor configuration and SOCKS endpoint, and required Tox TCP
recovery on a second independently observed three-hop circuit.

ADR 0192's content-free auxiliary observation also sampled four ordered states. Online reported
`tcp/reachable`; 35 ms after Tor loss it reported `tcp/refused`, preserving the provider's still-live
carrier label while exposing local route failure; authoritative offline reported
`offline/refused/blocked-by-local-boundary`; recovery returned to `tcp/reachable`. None of these
observations sampled a peer, changed the carrier projection, or advanced a session epoch.

ADR 0194's configured-target observation measured a complete SOCKS CONNECT in 266,385 us initially,
local proxy refusal in 67 us after Tor exit, and a recovered complete CONNECT in 237,701 us. Each
successful result was independently bound by authenticated control evidence to configured relay
zero and a new IoTox-owned SOCKS source. This closes the single-route target/circuit binding gate;
it still does not prove a Tox handshake or anonymity.

## Bound construction

The receipt binds Tor binary
`/nix/store/gacp048mx3m4q48gl5rlspw2j33328v4-tor-0.4.8.11/bin/tor`, SHA-256
`63055c572ff1ec2cb96b9ea4855804a06d06d26558609a028fa4d492e199c2b2`, and this normalized policy:

```text
AvoidDiskWrites 1
ClientOnly 1
ClientUseIPv6 0
CookieAuthentication 1
CookieAuthFile <RUN_ROOT>/control.authcookie
ControlSocket <RUN_ROOT>/control.sock
DataDirectory <RUN_ROOT>/tor-data
SafeSocks 0
SocksPolicy accept 127.0.0.1
SocksPolicy reject *
SocksPort 127.0.0.1:46501
```

`SafeSocks 0` is deliberate. The consumed c-toxcore SOCKS API sends numeric address records and
IoTox accepts only operator-supplied numeric relay records with native DNS disabled. Tor's
`SafeSocks 1` rejects numeric SOCKS destinations because it cannot distinguish an operator-supplied
address from one resolved unsafely by an application. It therefore rejects IoTox's leak-avoiding
input rather than strengthening it. Tor remains reachable only on loopback and rejects non-loopback
SOCKS clients.

The normalized configuration SHA-256 is
`b2c464565fd0793766243e0081d74e0501df7283e760cc5f2a168aac899a0478`. The source-linked IoTox
binary SHA-256 is `511b29744b5e0477e8da3277e109c998b030fb1d5890aebde3bddab28d41936f`.

## Measurements

| Observation | Result |
|---|---:|
| Initial Tox/Tor TCP | 9,120 ms |
| Initial configured-target CONNECT | 266,385 us; reply 0 |
| Initial configured-target circuit | 3 hops; `CONFLUX_LINKED` |
| Tor loss to local-boundary refusal | 35 ms |
| Local-boundary connect RTT at refusal | 67 us |
| Post-exit configured-target observation | proxy refused in 67 us |
| Carrier at local-boundary refusal | `tcp` |
| Tor loss to authoritative offline | 74,602 ms |
| Offline hold | 30,290 ms |
| Offline socket samples | 30 |
| Tor restart readiness to Tox/Tor TCP | 3,913 ms |
| Recovered configured-target CONNECT | 237,701 us; reply 0 |
| Recovered configured-target circuit | 3 hops; `CONFLUX_LINKED` |
| Total gate | 133,734 ms |
| Initial/recovered circuit hops | 3 / 3 |
| Initial/recovered Tor public TCP remotes | 3 / 2 |
| IoTox UDP sockets | 0 |
| IoTox direct-relay sockets | 0 |

The exact initial and recovered configured-target circuit paths are retained only as SHA-256
commitments `70592e480d48ed5a93a68bb45f5e79719df3c5d01da08bc1f761fff76e2e9ae2` and
`5dab5ee96304c8e27eb96f26d415c8913228de874770df71e0ade505fb7e207c`. Guard and exit addresses
are likewise retained only as socket-set digests. The slow loss transition agrees closely with the
generic SOCKS gate and remains c-toxcore connection truth, not a route-health target.

## Reproduction and verification

Obtain a current online numeric Tox TCP relay record independently, then run:

```sh
python3 tools/run-tox-operator-tor-smoke.py \
  --node IP:TCP_PORT:64_HEX_PUBLIC_KEY \
  --output operator-tor-receipt.json
python3 tools/verify-tox-operator-tor-smoke.py \
  operator-tor-receipt.json \
  --runner tools/run-tox-operator-tor-smoke.py
```

The runner refuses a dirty source tree, realizes the source-linked product, retains private logs
only on failure, and removes a successful run root. The canonical retained receipt is
`artifacts/rev0045/tox-operator-tor-smoke.json`, SHA-256
`508d85bf5f8098866005b030f1e2e7a5593276bdc1344c76cbad4ffc803b380f`. Its runner SHA-256 is
`57f8210342fa3aed2bb10676547e082406203763331ea4d6ebd9100601bf9928`; the independent verifier
SHA-256 is `4307a73042d6aadd5c7daa1eb7970c6c33e657c83c34efc939a4a49db6854d60`.

## Exact nonclaims

This is a single-host, single-Tor-build, single-public-relay, single-time-sample route gate. It does
not prove anonymity, resistance to traffic correlation or censorship, public-relay reliability,
multiple Tor exits or networks, two IoTox peers exchanging application traffic through Tor,
representative deployment behavior, or a service-level objective. The separate Sandwurm gate proves
two-IoTox application traffic through generic SOCKS; the two claims must not be silently combined
into an unrun two-peer actual-Tor claim. The 35 ms local observation does not define persistent
failure thresholds, terminal migration/resume policy, or upstream success while the listener is
reachable.
