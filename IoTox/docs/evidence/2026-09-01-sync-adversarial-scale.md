# Tree-v2 adversarial and scale qualification

Date: 2026-09-01

Status: accepted under ADRs 0280--0281

## Owned matrix

The source registry contains 718 selected unit/integration cases after this gate. New terminal-bound
rows are:

- 16 signed candidates at one path converge identically across 128 seeded arrival orders;
- a seventeenth candidate is refused at the protocol resource bound;
- 4,096 unique files complete scan, CAS installation, large-manifest identity, signed branch,
  merge, and projection;
- worktree recovery completes both durable exchange layouts and preserves an ambiguous locally
  edited tree; and
- a small manifest is explicitly equal to the former one-shot digest, proving ADR 0280 does not
  rename prior objects.

The existing owned rows cover same-writer forks, invented provenance, signed-store tamper, unsafe
paths/links, one-candidate-per-writer, all six three-writer orders, delete/edit conflict, explicit
causal resolution, pending checkpoint repair, exact cutoff retry, GC root closure, recoverable
quarantine/restore, and tampered quarantine refusal. The separate `iotox.sync-tree-process` test
forks and exits at all eight treepack projection durability points, then requires canonical retry.

The complete Clang ASan+UBSan preset passed all 68 registered targets: 16 owned-registry shards plus
the process, CLI, protocol-tool, and verifier surfaces. It selected the same 718 unit/integration
cases. Five delegated-cgroup targets returned their expected construction-host skip because the
development shell has no writable delegated cgroup; Sandwurm owns those kernel-backed gates.

## Multi-process evidence

The networkless three-writer Sandwurm receipt in
`2026-09-01-sandwurm-sync-three-writer-lifecycle.md` supplies 24 rotating post-conflict edits,
checkpoint propagation, pin/unpin, two-object quarantine/restore, one stopped/long-offline writer,
matching cutoffs on two survivors, and refused retired-writer re-entry. The two-hour real-directory
incumbent comparison is recorded separately in `2026-09-01-sandwurm-sync-resilio-shadow.md` and is
also the duration row for this matrix.

## Interpretation

The gate is complete at the protocol's explicit 16-candidate and 4,096-entry construction bounds
plus the same-machine Sandwurm lifecycle. Byte quotas remain independently validated policy fences.
This is not evidence for unbounded conflict populations, arbitrary Unix metadata, dishonest storage,
or formal crash consistency.
