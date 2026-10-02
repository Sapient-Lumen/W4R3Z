# Sandwurm Ratox total-route-loss evidence

Date: 2026-08-27

Status: accepted two-guest total-loss, detached-PTY, and exact-resume evidence on direct UDP,
forced TCP, and strict generic SOCKS; not automatic migration or actual Tor

## Claim

Two simultaneous source-linked IoTox guests opened one authority-bound Ratox PTY, exchanged a
heartbeat and byte `A`, then crossed seeded 100% egress loss on both task-owned TAPs. In every cell
the two-second heartbeat deadline expired while c-toxcore and the confirmed IoTox session retained
their original carrier and epoch. Roughly 28 seconds later the authoritative peer-offline event
produced the exact local `unavailable` outcome. While loss remained installed, the remote host
reported one live/running PTY, zero attached sessions, and a `peer-detached` journal entry naming the
same session.

After exact qdisc removal, each controller observed the same peer confirmed and authority-capable at
a higher online epoch, resumed only the prior session, preserved its process incarnation and byte
positions, advanced attachment generation from one to two, then completed a new heartbeat and byte
`B`. No new shell, automatic route migration, stale attachment acceptance, sequence reset, or
identity substitution satisfied the gate.

All roles used product revision `rev0045` and identical binary SHA-256
`511b29744b5e0477e8da3277e109c998b030fb1d5890aebde3bddab28d41936f`.

## Measurements

| Route | Heartbeat warning after loss | Authoritative offline after loss | Warning deadline to offline | Route restore to authenticated ready | Ready to resumed OPENED |
|---|---:|---:|---:|---:|---:|
| direct UDP | 2.187 s | 30.683 s | 28.261 s | 0.769 s | 21.123 ms |
| forced TCP | 2.248 s | 30.322 s | 28.062 s | 2.155 s | 48.940 ms |
| strict SOCKS | 2.139 s | 31.145 s | 28.873 s | 4.996 s | 28.034 ms |

The absolute online epoch happened to be 2 before loss and 3 after recovery in all three accepted
cells. The contract intentionally freezes only positive/stable before loss and strictly higher after
recovery: reused identities may experience an earlier harmless connection cycle during laboratory
startup, so absolute epoch 1 is not a valid product invariant.

| Route | Initial heartbeat / PTY | Recovered heartbeat / PTY | TAP drops | Compact proof |
|---|---:|---:|---:|---|
| direct UDP | 5.587 / 11.108 ms | 12.837 / 20.133 ms | 149 + 148 | `pair.0cnril1l` (228 KiB allocated) |
| forced TCP | 7.766 / 22.012 ms | 47.051 / 114.942 ms | 28 + 25 | `pair.qoty7j1x` (228 KiB allocated) |
| strict SOCKS | 6.524 / 31.939 ms | 5.720 / 21.254 ms | 26 + 46 | `pair.8jjawnwp` (1.3 MiB allocated) |

At 100% netem loss, `tc` correctly reports zero successfully sent packets/bytes and positive drops.
The drop counters—not post-disposition packet counters—are therefore the attempted-traffic witness.

The strict-SOCKS proof retains 655 client and 994 device egress IPv4 packets. Every retained packet
is TCP to `10.0.0.1:39050`; native UDP, direct-bootstrap, and direct-peer counts are all zero. The
forwarder admitted five connections to the sole configured target and denied zero.

## Evidence binding

| Route | Manifest SHA-256 | Lifecycle SHA-256 | Terminal capture SHA-256 | Heartbeat capture SHA-256 |
|---|---|---|---|---|
| direct UDP | `2077d4d51b2dab5add2bbd3edabee2db6e3b46820e0f820e1b666ce4c99d3970` | `f9a1667ed9849efd22d321c666d994847b18461bc127daf33846687e9f12d915` | `51168d2cbec6773ddfdf9307272f3bd0418dffce38e45e4331ba527c2c5163cb` | `f739a32cb5623a1680b07085a5c96be392ae2c4707d3eb11dc3365645b6f6717` |
| forced TCP | `e65a3042695079b24e6b5cc239b94e6d654b6df3099fd23085a5fa4950a414c7` | `0fa18e67cd2ea59c9b6c4ba93a77b2dc1e1e9feeed9183d258df9d27ba2fcc3d` | `42968716da2c96542ecee9c7945703a08949c3756a6837ee688a869a20a46da2` | `3c54f3bbd6f6a54b7f9a8139359323bfffefe1ed00dab3bdc200fe3246e6c99e` |
| strict SOCKS | `9d80bbd4d17898a1a336bebc34f3c71d2bf4cd1414b3de7d6c041270a8b478e6` | `9312ccc3f9212417b0d190632f42581eb1940cde203c08d17aac0a08643da3a6` | `319b2a2dabe40ca57e05ab777157e9e10ae8ef2a3e3e68a26f7eb4ee0701cdaf` | `1a008e6097069b5427b99945bb49f4c556d33e4f48663acdb9135e5a9b043d9b` |

The direct cell binds source revision `15b57aacd3a86df44896dff1b9a0557dbfc561dc`. The forced-TCP
and strict-SOCKS cells bind `4ba7a861db38bf3193cc106190ef63f571751e73`. Their complete diff is
one verifier allowlist line registering the scenario; guest construction and the binary are
byte-identical. Each private raw root was independently verified, exported through the exact
scenario allowlist, independently reverified, and then removed with the guarded workspace cleaner.

## Reproduction and verification

Run the exact three cells:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp ratox-route-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-route-loss
./tools/iotox-sandwurm-lab.sh up-pair tox-tor ratox-route-loss
```

For each returned private `PROOF_ROOT`, verify, compact, and reverify before cleanup:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair ROUTE PROOF_ROOT ratox-route-loss
python3 tools/export-sandwurm-pair.py PROOF_ROOT
python3 tools/verify-sandwurm-pair.py \
  --route ROUTE --scenario ratox-route-loss COMPACT_ROOT
```

Recheck the joined matrix and regenerate comparable timings:

```sh
python3 tools/analyze-ratox-route-loss.py \
  .sandwurm/exports/pairs/pair.0cnril1l \
  .sandwurm/exports/pairs/pair.qoty7j1x \
  .sandwurm/exports/pairs/pair.8jjawnwp
```

## Exact nonclaims

This is one construction host, one pair of guests per cell, one provider binary, one complete-loss
interval per route, and a fixed echo profile. It does not establish a latency or recovery SLO,
automatic reconnect, transparent route bonding, cross-route terminal migration, client-side input
prediction, Mosh-style screen-state convergence, long-duration process retention, multi-peer
fairness, physical-link diversity, or representative hardware behavior. The `tox-tor` cell proves
strict numeric generic-SOCKS containment through the laboratory forwarder. It is not actual Tor,
anonymity, circuit diversity, adversarial-proxy behavior, or two-IoTox public-Tor application
evidence. Those claims require their separately named gates.
