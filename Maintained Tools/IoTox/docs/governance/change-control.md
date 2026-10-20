# Change and revision control

## Before coding

- state the product slice and its acceptance evidence;
- identify decisions and invariants affected;
- decide whether the work belongs in core, tooling, research, or an incubator;
- for significant architectural additions, fill out
  `docs/architectural-change-intake.md`;
- avoid adding a dependency before its source, license, and maintenance cost are known.

## Before merging

- strict GCC and Clang build;
- focused tests for success and hostile failure paths;
- `iotox.docs-coherence` when front-door docs, topic help, authority examples,
  or architectural boundaries change;
- sanitizer/fuzz lane where applicable;
- active documentation and open questions updated;
- no claim promoted beyond the evidence;
- new durable choice recorded in an ADR.

## Before packaging

- increment `REVISION` and project version;
- update `BOOTSTRAPROSE.md`, changelog, package, manifest, build report, checksums;
- run the complete matrix available in the environment;
- test retained binaries independently of the source build;
- prove the lone-entrance layout;
- commit and verify a clean worktree;
- stage without `.git`, build trees, caches, or live identities;
- create the exact timestamped filename in America/New_York local time;
- extract the archive into a new directory and rerun the smoke facility.
