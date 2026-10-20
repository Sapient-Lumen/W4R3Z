# ADR 0283: accept the founding sync shadow and close the roadmap

Status: accepted, 2026-09-01.

## Context

ADR 0277 reduced repository completion to four gates executable on the founding machine and
permanently retired six gates that require hosted, independent-party, physical-target, or
independently witnessed public-history evidence. ADRs 0278 and 0279 closed selective synchronization
and route-policy population. ADRs 0280 and 0281 closed the finite tree-v2 adversarial/scale matrix.
The remaining obligation was an hours-long comparison with the incumbent synchronizer.

The first full-duration attempt exposed a real long-session defect: synchronization publishers kept
a finite non-evicting replay table and stopped admitting fresh reads after 256 retained results.
ADR 0282 replaced that lifetime budget with a bounded FIFO exact-replay window for authorized
immutable synchronization reads, without changing framing or weakening side-effecting replay rules.

## Decision

Accept compact proof `.sandwurm/exports/sync-shadow/run.XXdpLNPh` as the founding-machine
IoTox-versus-Resilio shadow gate. One networkless 2-vCPU/2-GiB Sandwurm/KVM guest ran a private
loopback c-toxcore bootstrap, two source-linked IoTox Agents, and Resilio Sync 2.8.1. A single seeded
mutation stream was applied independently to the IoTox and Resilio sources. For every cycle the
IoTox source, IoTox verified activation, Resilio source, and Resilio replica had to produce the same
canonical regular-file manifest.

The accepted receipt binds 240 cycles over 7,200,096 ms, six publisher and six replica Agent
restarts, zero post-setup manual publish/pull/activate commands, and 356 publisher replay-window
evictions. The positive eviction count proves useful operation beyond the exact boundary that
stopped the first attempt. The source-linked binary is bound to commit
`c24686f5229c1ed6a9b1d6822cd9cab85f011aa6`.

Together, ADRs 0278, 0279, 0281, and this decision close all four founding-machine gates. The
repository roadmap therefore has zero open completion checkboxes and six permanently struck
out-of-scope checkboxes.

## Consequences

For the bounded Linux regular-file model, IoTox may replace the incumbent synchronization path for
one noncritical directory when the operator accepts the documented limits and retains an independent
backup. This is a synchronization result, not a backup claim: valid deletions, tombstones, and
authorized changes propagate.

Completion does not add case-folding portability, symlink or rich metadata support, sparse remote
fetch, filesystem watching, incremental projection, invite/group UX, tree-v2 range or auxiliary
lanes, encryption at rest, permanent purge, physical power-cut evidence, hardware rollback
witnesses, independent-machine diversity, or production/security certification. Same-machine
Sandwurm evidence must continue to be named as such.

