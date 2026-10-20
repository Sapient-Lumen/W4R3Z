# ADR 0417: Add seed repository datacube profile

Date: 2026-10-01

## Status

Accepted.

## Context

IoTox now has two different handoff needs:

- a first public/GitHub repository seed that should be small, readable, and free
  of local experimental history; and
- a private provenance handoff that can carry full reachable Git history when
  that history itself is the point.

The existing `--public` profile was smaller than the `--upload` profile, but it
still used automatic history selection. That was correct for a bounded review
cube, but too easy to misunderstand as “the official public seed.” The upload
profile was even easier to misuse because its name sounds like the thing to put
on a hosting site, while it actually carries full local history and intentionally
has no default size ceiling.

## Decision

Add a first-class seed datacube profile:

```sh
tools/iotox-repo.sh datacube --seed
tools/make-repository-datacube.sh --seed
```

The seed profile:

- exports the exact tracked source tree from the clean commit;
- includes a cloneable `git/IoTox.bundle` containing one exact source-snapshot
  commit on a normal `main` branch by default;
- writes `git/HISTORY_MODE=snapshot`;
- omits local Git history;
- omits nested founding cubes unless explicitly overridden;
- keeps the same checksum, archive safety, symlink refusal, sensitive-path, and
  dirty-worktree gates as the other profiles; and
- uses the filename prefix `IoTox-seed-repository-datacube-...`.

Keep `--public` as the older automatic-history public profile and `--upload` as
the full-history private provenance profile.

## Consequences

- The recommended public handoff is now obvious and script-native.
- A GitHub seed can be rebuilt from the seed bundle without inheriting old local
  history, old failed experiments, or bulky Git pack provenance.
- Full history remains available when deliberately requested, but it is no
  longer the path the docs steer humans toward by default.
- The seed artifact is still an exact committed-state handoff, not release
  proof. `iotox ship-check` and the stable evidence sidecar continue to own
  product claims.

## Tests

- `bash -n tools/make-repository-datacube.sh tools/iotox-repo.sh`
- `tools/iotox-repo.sh release-plan stable`
- `tools/iotox-repo.sh datacube --seed /path/to/DR0Pbox`
- `tools/make-repository-datacube.sh --verify /path/to/DR0Pbox/IoTox-seed-repository-datacube-...zip`
- `git clone EXTRACTED/git/IoTox.bundle /tmp/IoTox-seed-clone`
