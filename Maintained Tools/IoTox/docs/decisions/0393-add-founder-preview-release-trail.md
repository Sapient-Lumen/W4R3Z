# 0393 — Add founder-preview release trail

Date: 2026-09-20

Status: accepted

## Context

ADR 0392 added the native product gate:

```sh
iotox ship-check [sync|terminal|all] [stable|founder-preview]
```

That makes the product claim executable, but a release still needs an ordinary
repository command trail. Without one, a founder-preview package could be cut
from memory, skip the stable brake, or drift from the datacube/export contract.

## Decision

Add repository companion commands:

```sh
tools/iotox-repo.sh release-plan [founder-preview|stable]
tools/iotox-repo.sh release-check [founder-preview|stable] [--iotox PATH] [--evidence-manifest PATH] [--allow-dirty]
```

`release-plan` is read-only and prints the exact command trail: doctor, build,
quick/full test, `ship-check`, stable brake, release check, source inputs,
datacube, datacube verification, cleanup audit, and the governing docs.

`release-check` is also non-packaging. It requires a clean worktree unless
`--allow-dirty` is explicitly used for rehearsal, runs whitespace and shell
syntax checks, verifies that the selected IoTox executable exists, runs the
selected native `ship-check`, and then enforces channel semantics:

- founder-preview must pass founder-preview `ship-check` and must still observe
  stable/no-concern blocked as expected;
- stable must pass stable `ship-check`, with an evidence manifest once ADR
  0395 is in force.

The native `ship-check` output and support-bundle plan now point at the
repository release trail.

## Consequences

The repo can be prepared for a founder-preview handoff without pretending that
stable/no-concern sync or Ratox have graduated. A future stable graduation must
make `iotox ship-check all stable --evidence-manifest PATH` and
`tools/iotox-repo.sh release-check stable --iotox /path/to/iotox
--evidence-manifest PATH` pass without weakening the current nonclaims.

The release trail does not run storage-media certification, recovery-custody
verification, external security review, or route diversity labs by itself. It only keeps the
release claim, local repository checks, and packaging plan aligned.

## Validation

- `bash -n tools/iotox-repo.sh`
- `tools/iotox-repo.sh release-plan founder-preview`
- native human CLI regression checks the new release-plan/release-check fields
- CTest includes a repo release-plan smoke
