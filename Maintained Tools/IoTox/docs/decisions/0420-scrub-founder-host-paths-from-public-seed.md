# ADR 0420: Scrub founder host paths from the public seed

Status: accepted

Date: 2026-10-01

## Context

Publication review of the seed repository at
`32051565b8ef98f44075051f6019ded05643b579` found no specific leaked credential,
but did flag avoidable founder-host paths such as an absolute Sandwurm checkout
and host Trash locations. The same review distinguished those paths from useful
laboratory evidence, public fixture addresses, hashes, public keys, and
security-control documentation.

## Decision

Public seed source should not publish avoidable absolute personal host paths.
The tree now uses:

- `git+file:../sandwurm` for the Sandwurm flake input and lock metadata;
- `SANDWURM_ROOT` in Sandwurm command examples;
- `$XDG_DATA_HOME/Trash/files` for discarded host Trash evidence locations;
- repository-relative or placeholder roots for workspace-local evidence paths.
- configurable CMake provenance labels so public standalone binaries do not
  embed the founder's absolute source/build directories.
- standalone build prefix maps and disabled build RPATHs so dependency source
  paths and local library search paths do not preserve the founder workspace in
  the shipped executable.

IoTox keeps the Sandwurm lab topology, dated engineering evidence, generated
run identifiers, resource measurements, and cleanup history when those details
are needed to understand claim scope.

## Consequences

The public seed is cleaner for inclusion in a wider repository without
pretending the qualification campaign happened on an anonymous generic machine.
Reviewers can inspect `docs/publication-boundary.md` for the publication rule:
scrub personal absolute paths, preserve useful technical evidence.
