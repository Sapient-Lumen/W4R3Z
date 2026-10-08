# Engineering Backlog

This file tracks high-leverage gaps for building Concord as a deterministic scientific tool.

## Highest Priority

- Formalize solver contracts between `gr_engine` artifacts and `grlab certify` outputs.
- Expand control tests for determinism and replay behavior across harness modes.
- Stabilize timing baselines (`goldens/timing_baseline.json`) with real p95 calibration runs.
- Add stricter schema validation coverage for critical artifact types.
- Replace single-metric extortion search with an anti-vampire scorecard (`avg_a`, payoff gap, recovery, repair abuse).

## Near-Term

- Improve search result provenance (search policy config and mutation parameters in outputs).
- Add more holdout suites for out-of-distribution robustness checks.
- Strengthen release posture (`gate-strict`) with installed security tooling in CI.
- Add machine-readable release manifest/checksum command for versioned bundles.
- Promote the new focal leave/rematch proxy into an engine-supported world to test partner-choice as a Golden-Rule stabilizer.
- Do not count `memory_one_exit` in a fixed dyad as “partner choice”; rematching / outside-option mechanics need their own world.
- Keep `mem1_exit_after_break_v1` as a compact rematch-world baseline and canonicalize unreachable post-exit parameters when search lands there.
- Add world-aware genotype-to-phenotype canonicalization before ranking rematch-enabled search results, because the current proxy shrinks 243 raw deterministic exit codes to 63 support-distinct families.
- Treat the current 63-family rematch quotient as a cooperative-pool lower bound; a single suspicious starter reopens it to 87 families, so canonicalization must be recomputed when entrant support changes.
- In the current deterministic no-noise proxy, reuse the rematch canonicalization cache only for entrant additions with C-only initial support; any entrant with initial D support should invalidate and trigger recomputation.
- Treat that start-support gate as zero-noise-only: any nonzero action tremble should invalidate the current cache and force recomputation under the active noise semantics.
- Use a mode-specific rematch cache key rather than one universal one: in the current proxy, opponent/bilateral tremble collapse to one quotient regime, focal tremble collapses to two, and only zero-noise remains heavily signature-sensitive.
- Do not keep the inherited `h=50` support-reachability bound in the current proxy: exact canonicalization saturates by `3/2/2/1` rounds across `{none, opponent, focal, bilateral}` noise modes, so unroll depth should be world-keyed and revalidated when semantics change.
- Compile the current proxy's canonicalization planner instead of keying on full entrant signatures plus `h=50`: the local exact plan shrinks key-depth budget from `12150` slots to `51/2/4/1` across `{none, opponent, focal, bilateral}` noise modes.
- In the current zero-noise proxy, replace the bulky `243`-entry `support_signature -> regime` dispatch table with the exact `17`-rule ordered wildcard classifier and regenerate it whenever world semantics change.
- Schema-check and contract-test that ordered classifier before vendoring it into any interim engine metadata.

## Operational Debt

- Generate `flake.lock` on a host where Nix works reliably.
- Add optional signed attestations on top of existing hash-based attest/verify flow.
- Improve docs for adding new probe registries and scorecard suites.
- Keep reading sources citation-first; do not let local PDFs regrow in the long-term archive.
