# Founding-machine route-policy population

Date: 2026-09-01

Status: accepted under ADR 0279

## Result

The content-free population receipt passed over the retained compact Sandwurm proof directory:

```sh
python3 tools/qualify-route-policy-campaign.py \
  --proof-root .sandwurm/exports/pairs \
  --evidence .sandwurm/route-policy-campaign-20260901.json \
  --seed 20260901
```

Receipt SHA-256: `dbd56071307e089cd1192441733fedfd5b752a0ffcff3113de57599b0d11984b`.
The receipt binds the proof-manifest set as
`51cfd75d90995de24e0b529ed4e1c58f1657722dc98b937d6f98ffe81c9e7d17` and the seeded
schedule as `445cffcd206ae3df93da9ae50fa63a65fa63bf159d8cc6a03beed2d87069fe5f`.

| Measure | Accepted value |
|---|---:|
| integrity-checked cells | 16 |
| carrier classes | direct UDP, forced TCP |
| cumulative whole-VM observation | 9,814,432 ms (2 h 43 m 34.432 s) |
| exact timing strata | 250, 500, 750, 1,000, 5,000, 20,000 ms |
| artifact strata | 131,369; 524,355; 1,048,643; 4,194,601; 16,777,283 bytes |
| ABBA phase durations | 16 samples, 76,430--94,290 ms |
| adaptive/fixed aggregate ratio | 1,055,522--1,167,986 ppm |
| process-resource commitments | 22 |
| exact binary commitments | 6 |

The seven scenario classes are corresponding readiness order, degraded startup admission,
population loss, simultaneous loss/cancel, loss-first/cancel-later, shared-link contention, and
counterbalanced throughput. Each included proof has an exact compact-file set, two matching passed
role receipts, and a passed pair manifest. Private guest disks, identities, keys, and payload bytes
are not in the campaign receipt.

## Interpretation

This is a stratified population, not a claim that the historical faults were randomly timed. The
published seed makes evidence ordering independent of directory order and prevents cherry-picking;
exact strata make the important race linearizations reproducible. Adaptive selection won every
accepted aggregate throughput observation, so it becomes the ordinary initial-admission policy.
The range is not a performance SLA and does not prove two physical paths, strict QoS, bonding, or
public-relay independence.
