# Meta: Kernel Artifact Schema Protocol (rev0488)

## Purpose
Use this protocol when the repo is deepening an already-earned top-band kernel from:
- contract prose,
- witness examples,
- and replay fixtures

into a **machine-validatable schema family**.

This protocol is not for:
- broad ranking or reranking,
- kernelization of new candidates,
- schema-writing for `hold` candidates,
- or pretending rendered markdown/operator notes must all become JSON immediately.

Read with:
- `design/epic-contribution-kernel-artifact-schemas-2026Q1.md`
- `design/epic-contribution-kernel-interface-contracts-2026Q1.md`
- `design/epic-contribution-contract-witness-packs-2026Q1.md`
- `design/epic-contribution-kernel-fixture-packs-2026Q1.md`

## When a schema pass is justified
A schema-governed revision is justified when all of these are already true for the target kernel:
1. it has a live decision packet;
2. it has a bounded v0 kernel brief;
3. it has a slice-0 note;
4. it has a contract0 note;
5. it has witness/example outputs;
6. it has at least one fixture card naming replay inputs and expected checks.

If any of those are missing, deepen the missing earlier layer first.

## Required outputs for a schema pass
Every schema-governed revision should add or refresh:
1. one design note explaining why schema-writing is justified now;
2. one meta protocol (this file or its successor);
3. a schema corpus directory with README;
4. a hygiene/index file that names required schema families and witness bindings;
5. example specimen payloads for any new schema families introduced;
6. one machine checker that validates specimens against schemas;
7. archive-doctor/hygiene wiring so the new checker becomes part of repo maintenance.

## Required fields for each schema file
Every schema file should include at minimum:
- `$schema`
- `$id` (local archive identifier is fine)
- `title`
- `type`
- `required`
- `properties`

Default posture:
- use additive/open compatibility (`additionalProperties: true`) unless there is a strong reason not to;
- require only the core fields that the contract/witness/fixture stack already earned;
- keep enums bounded only where the archive truly depends on them; and
- avoid freezing every possible future nested field.

## Required fields for the schema hygiene/index file
The first hygiene/index file should include:
- schema family marker
- revision
- required schema families
- schema family to specimen binding map
- refused moves

## Binding rule
Every schema family added in the first top-band corpus should bind to at least one specimen payload, unless the revision explicitly says why the family is intentionally schema-only for now.

Every specimen payload validated by the checker should:
- declare `schema_family`;
- point to a schema family present in the corpus;
- remain illustrative rather than pretending to be live evidence;
- and preserve negative/unsupported/stale posture where the contract requires it.

## Shared receipt rule
Prefer shared receipt schemas for recurring cross-kernel states such as:
- `unsupported-state-receipt/v0`
- `stale-card-receipt/v0`

Do not fork near-identical receipt families per kernel unless the meaning genuinely diverges.

## Validation rule
A schema pass is incomplete unless the repo-level checker:
- finds the required schema files,
- loads them successfully,
- validates bound specimen payloads successfully,
- and fails loudly when a bound specimen or schema disappears.

## Refusal rules
Do not:
- write schemas for `hold` candidates just to make the repo look more complete;
- treat schema presence as proof that upstream Rust/Cargo should adopt the family;
- over-tighten schemas until additive evolution becomes impossible;
- or use schema-writing to hide negative states that were explicit in witnesses or fixtures.

## Exit criteria
This protocol has done enough for a kernel when:
- the first JSON artifact families have schemas;
- witness payloads validate cleanly;
- unsupported/stale/shared receipt posture is machine-visible;
- and future revisions can tell whether an example payload drifted structurally instead of merely aesthetically.
