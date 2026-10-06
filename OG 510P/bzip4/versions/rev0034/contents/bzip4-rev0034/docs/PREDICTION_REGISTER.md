# bzip4 falsifiable prediction register — rev0034

These are forecasts, not release claims. They make the next sessions easier to
evaluate without moving the goalposts after seeing new cubes. Percentages refer
to elapsed time unless stated otherwise.

| ID | Prediction | Confidence | Test that resolves it |
|---|---|---:|---|
| P1 | On the next rotating Datacube-like cohort, matched Clang `-O3` bzip4 at 1 MiB / up to 8 lanes will have median encode and decode time 3–12% below pristine bzip3 1.5.3 at the same partition and lanes. Individual specimens may tie or regress. | 65% | At least 5 interleaved rounds, whole-cohort and per-cube, same compiler/flags/affinity/publication accounting. |
| P2 | `cloudtainer-speed-v1` will be the fastest tested profile or within 10% of the fastest encode-plus-decode total on mixed future cube cohorts. | 70% | Compare 256 KiB, 512 KiB, 1 MiB, 2 MiB, and 4 MiB with runtime lane fitting under 128 MiB. |
| P3 | `cloudtainer-balanced-v1` will be 6–15% smaller than `cloudtainer-speed-v1`, while its combined encode/decode time remains within 15% on sufficiently large payloads. | 65% | Per-cube and combined-stream profile comparison on the next two rotating cohorts. |
| P4 | Raising active outer lanes beyond eight on a similar dual-channel cloudtainer will improve throughput by less than 15% while increasing charged workspace by at least 35%. | 75% | Fixed 1 MiB block, 8/12/16 active lanes, hardware counters and process HWM. |
| P5 | A carefully ported current libsais release has a 55% chance of improving at least one direction by 3% or more without ratio change; the plausible range is 2–10% encode and 0–8% decode. | 55% | Isolated old/new libsais A/B, identical compiler/profile/input, strict byte and sanitizer gates. |
| P6 | Profile-guided optimization will improve each hot direction by 2–8% more often than IPO alone, but has less than a 50% chance of exceeding 5% in both directions. | 45% | Train on one rotating cohort, evaluate on a different unseen cohort, compare reproducible builds. |
| P7 | Reusing a linked or retained bzip4 service will cut end-to-end latency for 1–3 MiB capsules by 10–30% relative to spawning the static CLI per operation. | 60% | Warm and cold process/service benchmark including startup, state construction, fsync, and output verification. |
| P8 | A trained dictionary will not improve both encode and decode speed under the same memory budget; probability of a qualifying speed win is below 20%. | 80% | Only reopen with prepared shared dictionaries, charged dictionary bytes, and unseen holdout timing. |
| P9 | Recommended 1 MiB and 2 MiB profiles will remain below 200 MiB process RSS for a single operation on similar cloudtainers, leaving substantial room beneath a nominal 3 GB ceiling. | 90% | `/usr/bin/time -v`, cgroup HWM, and planner receipt across encode/decode and incompressible data. |
| P10 | Blocks at 64 MiB and above will remain poor automatic speed choices; 256 MiB decode will remain operationally unacceptable until a specific pathological loop is repaired. | 85% | Cycle profile and bounded-time decode across repetitive, random, and current cube-derived streams. |

## Decision consequences

P1–P4 support the present production policy: Clang convenience binaries,
1 MiB general speed blocks, 2 MiB only by explicit balanced profile, and a
runtime cap near eight useful lanes. P5–P7 identify the likely next speed wins.
P8 keeps dictionary work frozen. P9 is the memory safety expectation, while P10
prevents ratio enthusiasm from silently selecting giant blocks.

A prediction is considered failed when its specified test falls outside the
range, even if a different metric looks favorable. Machine-readable entries are
in `evidence/prediction-register.json`.
