# Sandwurm later-window actual-Tor Ratox repetition

Date: 2026-08-29

Status: accepted two-IoTox actual-Tor duration/circuit-churn repetition; operator-date record, not an
independently witnessed time or exit-operator claim

## Claim

Compact proof `.sandwurm/exports/pairs/pair.wbsef5tp` binds two source-linked Sandwurm guests, two
independent Tor 0.4.8.11 processes, the public numeric Tox record `144.217.167.73:33445`, and one
authority-bound Ratox echo session. The client completed 120 paired terminal and heartbeat samples
at a one-second interval while the host requested closure of the exact client circuit after sample
20 and the exact device circuit after sample 100.

| Checkpoint | Tor result | Recovery | Ratox result |
|---|---|---:|---|
| client, ordinal 20 | new stream and distinct three-hop path | 12.267 s | attachment continuous; epoch 2/generation 1 |
| device, ordinal 100 | new stream and distinct three-hop path | 27.999 s | authoritative loss; explicit epoch-3/generation-2 resume |

Both raw close events report `REASON=REQUESTED`. Tor, IoTox, the guests, and the retained PTY host
process have zero restarts. Exact terminal positions advance through 21 and 101 in their respective
branches. Active sampling lasts 353.783 seconds; maximum terminal/heartbeat round trips are
2.992/4.896 seconds. These are observations, not deadlines or an SLO.

## Containment and path population

The client and device captures contain 2,546 and 3,118 IPv4 egress packets. Every packet is TCP to
the exact role-local Tor listener. Native UDP, direct bootstrap, direct relay, and direct peer counts
are all zero. Their pcap SHA-256 values are:

```text
d413f7aea7e8db7528738b7108d6ae36c44edea8e20b18cd1aad1c123a025cad
a10d8540d19ee8483618379c3f6114c69071ad974ada4fd145b086c290bc8e80
```

The deterministic eight-proof population report now records 30 exact target/churn declarations,
24 unique normalized three-hop paths, 20 first hops, 23 last hops, and 24 first/last pairs. This
proof contributes four unique paths and four last hops with no complete path, first hop, or last hop
shared with any preceding proof. The report remains content-free and explicitly refuses an
independent exit-operator or time-window claim.

## Reproduction and exact proof

```sh
./tools/iotox-sandwurm-lab.sh up-pair tox-tor \
  ratox-route-actual-tor-soak \
  144.217.167.73:33445:7E5668E0EE09E19F320AD47902419331FFEE147BB3606769CFBE921A2A2FD34C
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/lab/pairs/PAIR_ID ratox-route-actual-tor-soak
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/exports/pairs/PAIR_ID ratox-route-actual-tor-soak
```

The raw and compact manifests, churn record, lifecycle record, and compact-export SHA-256 values are:

```text
aef6d7971d34181883a00697ed2e45e48c032de9b18082660bffea6c188a5c77
0eb735f0b69c2f59253a96e7446267043c400906c3a88208e5677e75c461c8e3
fe128a32bac118a30c4e32bdbb9d7652e4183a6eb48aecfea1294b9aa7361b3b
7de02b40fd7966e857e8013d65e088235c8131d4cc86152ec1dd3b4a7e9973fc
214a2a562642f83a5acf5b9b65131ccfc1793eb5366c27b544811925badf6dc0
```

The raw rendezvous span is 932,891,205,486 ns. The compact export allocates 3,325,952 bytes and
declares `contains_secrets=false`; guest disks, injected identities, runtime state, bootstrap secret,
and Tor data directories remain private. Both forms pass strict verification.

## Nonclaims and next gate

This is one host, two local VMs, one public endpoint, one echo profile, one Tor build, and one later
operator-selected run. It does not prove an independently witnessed UTC interval, independent exit
operators, jurisdiction/AS diversity, anonymity, unlinkability, availability, an SLA, target-fleet
behavior, or automatic migration. The next M8 experiment must bind its campaign window in the proof
schema and review the last-hop operator population separately from content-free path counting.

