# Jobsets and build farms (Hydra lessons, DeriveBSD-native)

DeriveBSD needs a way to continuously populate caches, run tests, and promote artifacts into channels.
Nix solved much of this operational problem with **Hydra**, whose central abstraction is the **jobset**: a declared set of build jobs evaluated and built repeatedly.

DeriveBSD should steal the operational abstraction while keeping evaluation deterministic and code-free.

## Terms

- **jobset**: “the set of targets we continuously evaluate/build/test for a channel.”
- **evaluation**: produce Lock/Plan objects for a repo revision under an explicit policy.
- **build**: execute Plans on a builder pool (jails or microVM builders), produce artifacts + evidence.
- **promotion**: move artifacts/evidence into a signed channel snapshot.

## DeriveBSD jobset contract

A jobset definition is canonical data:

- input source (repo, revision selection)
- target matrix (arch/ABI, host/workload kinds)
- policy profile (which gates apply, which evidence required)
- promotion rules (what must pass before a snapshot is signed)

The **policy decision record digest** is part of the identity chain, so “what was allowed to build/promote” remains auditable.

## Minimal v0 workflow

1) Evaluate
- produce Locks/Plans for the jobset at revision R
- record an `evaluation.receipt` (repo digest, policy digest, produced Plan digests)

2) Build + test
- build Plans on builder pools
- emit artifacts + `test.receipt` (optional but strongly recommended) (see `docs/166-test-receipts-and-promotion-gates.md`)

3) Promote
- produce a signed channel snapshot referencing artifact digests + required evidence
- publish through the existing cache/publish domains

## Why steal “jobsets” specifically

Jobsets clarify the difference between:
- “these are the bytes” (targets)
- “these are the builds we require before promotion” (quality gates)

Hydra’s docs emphasize projects+jobsets as the unit of evaluation/build scheduling.

## Relation to remote execution / builder pools

Jobsets don’t require remote execution, but they benefit from:
- scalable build workers
- shared action/result caches
- consistent sandbox construction

See: `docs/136-remote-execution-api-builder-pools.md`.

## References

- Hydra repo docs (projects/jobsets): https://github.com/NixOS/hydra
- NixOS wiki: Hydra overview: https://wiki.nixos.org/wiki/Hydra
- Hydra paper (Dolstra): https://edolstra.github.io/pubs/hydra-scp-submitted.pdf

Last updated: 2026-02-23
