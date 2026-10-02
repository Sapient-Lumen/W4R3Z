# Sandwurm strict Tox/Tor route evidence

Date: 2026-08-27

Status: accepted two-guest generic-SOCKS route evidence; not actual-Tor evidence

## Claim

Two simultaneous KVM/Sandwurm guests ran the exact source-linked IoTox 0.45.0 rev0045 binary from
clean source revision `830a2749d288aa6d4da88994c6e47db4aec24124`. Both reused the immutable
private test-identity baseline, projected `Tox/Tor`, and reached the pinned host-bridge c-toxcore
0.2.23 bootstrap/TCP-relay fixture only through the bounded numeric SOCKS5 endpoint
`10.0.0.1:39050`.

The guests established friendship, a confirmed IoTox session, and bidirectional text without a
private-L2 ping. The host then killed the proxy. Both peers reported offline, the proxy restarted on
the exact endpoint, both peers advanced from online epoch 1 to epoch 2, and fresh bidirectional text
crossed the recovered session.

## Packet and proxy observations

Each TAP capture began before the reusable identities were released to its guest. The verifier-bound
summary is:

| Role | IPv4 egress packets | Allowed destination | UDP | Direct bootstrap | Direct peer | Capture SHA-256 |
|---|---:|---|---:|---:|---:|---|
| client | 474 | `10.0.0.1:39050/tcp` | 0 | 0 | 0 | `e678be1a515eb708a2dc7bf323c1c41040f417c4771f3109eb0a263c6bd3322c` |
| device | 439 | `10.0.0.1:39050/tcp` | 0 | 0 | 0 | `4932f0056e92dfaba14df5d340c5e0ba2143297920bc74db85050dff160cdc5c` |

The initial and restarted proxy phases each admitted exactly two requests to the only allowlisted
target, `10.0.0.1:33445`, and denied zero. Their audit SHA-256 values are
`a9eb1146a3d092679900d22b8fa2558ec9b5fedde3d2606ed9fdf6c1db5b09a0` and
`a1a5a085b97c7ae68a700c51cbab08a69f857f2224924695a332ed2f1dcca331`.
The last initial admission and first restart admission are 99.608 seconds apart; this is an upper
envelope containing pre-fault session work and loss detection, not a proxy-outage latency sample.

Both guest receipts bind IoTox SHA-256
`6169668000a1462322cc2cdd9b743ebd06fc5ee8e5721b19747292b9e227e6b0`. Client/device receipt
SHA-256 values are `895ee928a01b7ea285323539f572b8f690beb3375bd83471a6b7d4edca65390c`
and `319baed65d2b1b55a647173d6f159d6cb809262f126a5425e302a7f1ed4c14ca`.
The complete host span, including clean image realization, was 507,076,045,637 ns.

## Proof and reproduction

The accepted private source was `pair.zyy913jf`. It contained writable guest disks, injected test
identities, runtime state, and the bootstrap secret. After compact verification those reproducible,
owner-private artifacts were removed by the guarded zero-retention cleaner.

The accepted compact proof is `.sandwurm/exports/pairs/pair.zyy913jf`. It allocates 704,512 bytes,
omits those private artifacts, and retains the two encrypted packet captures and their network
metadata. Its source-manifest SHA-256 is
`63195c7ab64ea257d1010d33cd2f02db7b7c58eeb5c81d6a33a3044130f45d38`; compact pair-manifest
SHA-256 is `46a9fcdf52c04063c37edb4dfc47dc4300cb3e1b34885ef6d0fd90ea6616ff8c`; and
`compact-export.json` SHA-256 is
`51c038ee4f4fd6f242b7afe2c9893b8a7ff3a1ecdbac67f58858eb3a6a93fbe9`.

```sh
./tools/iotox-sandwurm-lab.sh up-pair tox-tor proxy-restart
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/lab/pairs/PAIR_ID proxy-restart
./tools/iotox-sandwurm-lab.sh export-pair \
  .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/exports/pairs/PAIR_ID proxy-restart
```

Both the uncompacted and compact accepted proofs independently returned
`iotox.sandwurm-pair-verification.v0` with status `passed`.

## Exact nonclaims

The proxy is the auditable laboratory forwarder, not Tor. The proof establishes the strict generic
SOCKS construction, two genuine IoTox peers, packet containment on the stated TAPs, proxy
loss/recovery, and restored application traffic. It does not establish a Tor circuit, anonymity,
public relay reachability, censorship resistance, long-running route reliability, or an operator
Tor configuration. Those are separate M8 gates. The later accepted operator-Tor/public-relay sample
in `2026-08-27-operator-tor-public-route.md` closes its own bounded route gate without retroactively
turning this generic-SOCKS pair into actual-Tor evidence.
