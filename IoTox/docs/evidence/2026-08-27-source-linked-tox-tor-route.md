# Source-linked strict Tox/Tor construction evidence

Date: 2026-08-27

Status: accepted construction evidence

## Claim

The exact clean source revision
`3c7ee7aa0f6f628edc0c59d8a70083fd87975b0a` realized IoTox 0.45.0 rev0045 and the pinned
c-toxcore bootstrap fixture, then reached TCP self-connectivity through one bounded numeric-only
SOCKS5 forwarder. Linux process/socket ownership showed that IoTox opened TCP only to the proxy,
owned no UDP socket, and opened no direct TCP socket to the relay. After the proxy was killed,
IoTox eventually reported `offline` without opening a native bypass. Restarting the exact same
proxy endpoint admitted a second forward and restored TCP connectivity.

The machine-readable result is [the rev0045 receipt](../../artifacts/rev0045/tox-tor-smoke.json).
Its SHA-256 is `cbb54c259ed5ef57270c7025adb43270e46bba0375df73f7a78c2c9ce70fa4d4`.

## Measured lifecycle

| Measurement | Result |
|---|---:|
| initial construction to TCP | 8,038 ms |
| proxy loss to c-toxcore `offline` | 77,993 ms |
| exact-endpoint restart to TCP | 4,921 ms |
| complete gate | 91,178 ms |
| initial admitted/denied proxy requests | 1 / 0 |
| restart admitted/denied proxy requests | 1 / 0 |
| native UDP socket observed | no |
| direct relay socket observed | no |

The accepted receipt binds:

- IoTox SHA-256 `6169668000a1462322cc2cdd9b743ebd06fc5ee8e5721b19747292b9e227e6b0`;
- pinned bootstrap SHA-256 `9ce88ccc2edfcb817f6123f87de8927ff2c7737e9ebde4d70bb11070dd144ebb`;
- forwarder SHA-256 `4ee24c68724ed03c2815ad1fd098c9bdbf96aa44173f5316dde0a98a1d42539b`;
- gate SHA-256 `e5c59f3632e1bea06445d3eca11ae371c109b25acfaf07240b6464f6fc819235`;
- network `Tox/Tor`, carrier `tcp`, and DNS policy `disabled-numeric-only`.

## Failure-detection finding

Recovery after the endpoint returned was fast enough for this construction gate, but a nearly
78-second loss indication is not acceptable as the only user-visible signal for a future
Eternal/Mosh-style terminal. The pinned provider defines `TCP_PING_FREQUENCY` as 30 seconds and
`TCP_PING_TIMEOUT` as 10 seconds; relay/onion state and reconnection add further scheduling. Those
constants explain the coarse timescale, but this single observation does not attribute every
millisecond or establish a distribution.

IoTox must not report the Tox carrier offline before c-toxcore does. The follow-on design therefore
keeps provider connection truth unchanged and adds a separate, content-free route-health and
application-liveness signal for admission, scheduling, and terminal UX. It must distinguish a dead
local proxy, an unreachable upstream, and an application heartbeat miss, and it must not reset a
session epoch merely because the auxiliary health signal degrades.

## Reproduction

From an exact clean tree at the bound source revision:

```sh
python3 tools/run-tox-tor-smoke.py \
  --output artifacts/rev0045/tox-tor-smoke.json
(cd artifacts/rev0045 && sha256sum -c SHA256SUMS)
```

The gate refuses a dirty source tree so that its commit and tool digests are meaningful.

## Exact nonclaims

The laboratory forwarder is not Tor. This proof does not establish a Tor circuit, anonymity,
public relay reachability, Sandwurm TAP containment, two-peer application traffic, long-running
reconnect behavior, or production readiness. The receipt deliberately labels itself
`source-linked-local-construction-not-actual-tor`. Those are separate M8 gates.
