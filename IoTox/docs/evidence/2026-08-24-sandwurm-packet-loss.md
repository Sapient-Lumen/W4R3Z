# Sandwurm seeded partial-loss evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests stayed connected and exchanged ordinary bidirectional
text while both private TAP receive paths were independently impaired by seeded random 5% packet
loss. Each guest emitted 128 exact 1,200-byte Tox lossy custom probes at 5 ms spacing, retained one
canonical row per ordinal, incurred no local send rejection, and remained at confirmed online epoch
1. The runner observed positive kernel packet and drop counters on both TAPs before removing the
qdiscs; both peers then exchanged fresh text over the restored route.

## Accepted cells

| Route | Compact proof | TAP packets/drops | Client delivered/missed | Device delivered/missed | Median RTT client/device |
|---|---|---|---:|---:|---:|
| direct UDP | `.sandwurm/exports/pairs/pair.2cshb1og` | 312/17, 311/17 | 119/9 | 117/11 | 9,729 / 9,585 us |
| forced TCP | `.sandwurm/exports/pairs/pair.d36fjp4k` | 277/12, 282/14 | 128/0 | 128/0 | 30,354 / 31,465 us |

The direct-UDP delivered samples had client/device p95 RTT of 28,000/28,961 us and maxima of
39,064/39,827 us. Forced TCP had p95 RTT of 80,356/97,142 us and maxima of 86,913/106,783 us.
These are construction-host observations from one bounded burst, not latency service objectives.
The zero forced-TCP application misses coexist with 26 kernel drops and therefore demonstrate
lower-layer retransmission rather than an inactive impairment profile.

Both cells used binary SHA-256
`829ec298709f831899a37ec1abd062b3755fedbdb717d67b80e0768e5689dda3` and the immutable reusable
test-identity baseline. Direct-UDP and forced-TCP spans were respectively 389,200,973,127 ns and
317,131,887,749 ns. Their compact pair-manifest SHA-256 values are
`f6e325530aeb415e5ef67a05974827a87effa8612d2c7870cb89101a3f23d208` and
`597c6bbe6b4d91adf7bc8421970d206c62d5eec010c96550e9160a19b73136b6`; compact-export declaration
SHA-256 values are `d379dc03cae740edb3719941b193b8d713dddd4d7237a2d02385f4b2e87c5a6e` and
`8acded21f81e20b77c8e7b8c9e9099c9d2b4e40c0175a230d1089a0221a33c95`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp packet-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp packet-loss
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.2cshb1og \
  --route direct-udp --scenario packet-loss
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.d36fjp4k \
  --route forced-tcp --scenario packet-loss
```

The raw proof roots contained private writable guest disks and injected test identities. They were
removed only after compact export and strict reverification; they are recoverable by rerunning the
fixture.

## Exact nonclaims

This does not establish public-network behavior, a provider upgrade, a second physical machine,
multiple loss rates or seeds, burst-loss behavior, delay/jitter/reorder/duplication, Ratox PTY
keypress-to-render latency, an SLA, or fitness for an arbitrary deployment network.
