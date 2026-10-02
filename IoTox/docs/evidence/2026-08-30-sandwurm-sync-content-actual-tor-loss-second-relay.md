# Sandwurm selected actual-Tor content-worker loss, second relay — 2026-08-30

## Claim

The ADR 0260 destructive content-v2 gate repeats through a second compiled public Tox TCP-relay
record. One selected auxiliary Tor worker disappears after positive object progress; the atomic job
fails whole without reassignment, downgrade, accepted HEAD, or activation; the same signed route
recovers under a fresh worker incarnation; and only a distinct explicit pull converges.

This is a bounded relay-record-diversity result for ADR 0261. It is not exit/operator diversity,
independent physical-path diversity, anonymity, availability, long-running stability, or a
performance claim.

## Construction

Two simultaneous Sandwurm Cloud Hypervisor guests retain native authority sessions while two exact
`tox/tor` workers per side use separately attributed host Tor processes. Both Tor instances target
the explicit public record:

```text
205.185.115.131:443
3091C6BEB2A993F1C6300C16549FABA67098FF3D62C6D253828B531470B53D68
```

The selected second signed bulk member remains
`478CD68E0D2035CD1B63CC07558070EBEA7897DAB135896115BB85B524E23C1A`. The subscriber's lab-only
fault selector stops only that in-process worker after at least 65,536 exact-carrier receive bytes.
It does not stop an Agent, Tor process, VM, or native primary session.

## Invocation

```sh
python3 tools/run-sandwurm-pair.py direct-udp \
  sync-content-multi-route-actual-tor-loss \
  --tor-node \
  205.185.115.131:443:3091C6BEB2A993F1C6300C16549FABA67098FF3D62C6D253828B531470B53D68

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/lab/pairs/pair.i8ar90tx \
  --route direct-udp \
  --scenario sync-content-multi-route-actual-tor-loss

python3 tools/export-sandwurm-pair.py \
  .sandwurm/lab/pairs/pair.i8ar90tx \
  .sandwurm/exports/pairs/pair.i8ar90tx

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.i8ar90tx \
  --route direct-udp \
  --scenario sync-content-multi-route-actual-tor-loss
```

## Accepted observations

- scenario `sync-content-multi-route-actual-tor-loss`, route mode `direct-udp`, status `passed`;
- stopped worker `17305418366285522271`, recovered worker `9399449097838626368`;
- 76,776 exact-carrier bytes at the fault, above the 65,536-byte threshold;
- first job `5356260296355692902`, replacement job `2192547647293893774`;
- two committed immutable objects and 528 fetched bytes before whole-job failure;
- one carrier loss, zero reassignment, one worker recovery, clean staging, no accepted HEAD, and no
  activation from the failed job;
- native primary and secondary authority epochs remained `1/1`;
- the explicit replacement pull received five primary-source and two secondary-source objects;
- artifact SHA-256
  `844dbd0270ee58cf1e1b8062460e6b5f24b974a24fd482e861689d65e81598a7`, manifest SHA-256
  `f8637c280348a3af9685afdbb53a0351236ec52e26abb146ec8f3a20c39c9b66`, and accepted HEAD-record
  digest `5418cf893bf66afe955edf1b855e9e72c4069693d245fef9a579f8917c02141c`;
- two actual Tor 0.4.8.11 instances at 100% bootstrap with distinct three-hop application-circuit
  commitments;
- five successful client-guest and three successful device-guest exact-target source streams;
- client TAP: 3,768 proxy, 2,378 native UDP, 39 native relay-TCP, and zero unexpected-context
  packets;
- device TAP: 5,025 proxy, 3,952 native UDP, 82 native relay-TCP, and zero unexpected-context
  packets; and
- identical source-linked binary SHA-256
  `efc0b415f4198a67949ab7fce70b5c30f83c6cff3c6b69d4262b46ba9674fa04` in both guest receipts.

## Independent verification and retention

The first independent raw verification rejected the host manifest because
`multi_source_loss_head_fenced_role_count` was zero. Both completed guest receipts independently
recorded `multi_source_loss_head_fenced=true`; the copied runner allowlist covered native
multi-source loss but omitted routed actual-Tor loss. The runner now uses one frozen
`CONTENT_MULTI_SOURCE_LOSS_SCENARIOS` set for every common loss field. Only the derived manifest
count was rebuilt to `2`; no receipt, checkpoint, capture, guest disk, or product artifact changed.
The unchanged strict verifier then accepted the raw root and compact export.

- compact pair-manifest SHA-256:
  `7a5e235ca2ead66d4052186d4f9f5f7fa3499ac687bab4f5754315f8163bb932`;
- compact-export record SHA-256:
  `fa68af587bf1eb6e63c889ed769a1e85c7eb18e3c3d4945fbebb37af456dd7f4`;
- client receipt SHA-256:
  `3a322f424c4de7f989e2e746d3c66c29ef0966620d34c476ecc32c2ee304b37a`;
- device receipt SHA-256:
  `ebe6d3fe33ea198d2f70acafafe27fb2ffeabdae1b3033af2bdc0c3908459811`;
- client capture SHA-256:
  `f755ab7cca337157d6664b36df326ac7daee4f1285433f563dd98347d23bcea0`;
- device capture SHA-256:
  `96b843495efebc4d657756c60d51e2236ec2e2d318779cfd9ff365350896163b`;
- compact allocated bytes: 15,286,272; files: 23.

The compact export retains the exact verifier surface: receipts, loss/recovery checkpoints, pair
manifest, authenticated Tor bootstrap/circuit/control evidence, TAP captures/logs, and both
Sandwurm chain records. It contains no private writable guest disk.

## Limits and next gate

This repeats one safety gate through a second public relay record. It does not prove independently
separated exits or time windows, relay availability, long-duration policy, independent bottlenecks,
or useful striping. Gate 5 remains a campaign: randomized startup/fault distributions, cold absent
routes, startup during real faults, repeated larger-object measurements, disk-pressure refusal,
configuration replacement, clean shutdown, and hours-long churn. ADR 0262 subsequently qualifies
bounded same-source two-object scheduling over native UDP and forced TCP. Comparative lane-count
bottleneck science, byte/route striping, and multi-lane daemon restart remain open.
