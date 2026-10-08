# Database schema lineage

## Two independent version axes

Lacuna versions two different things:

- **event schema** governs immutable event envelopes and payload interpretation;
- **database schema** governs SQLite tables, indexes, and replayable projections.

The current runtime keeps event schema 1 and database schema 8. A physical migration may add or rebuild projections and migration custody, but it must not rewrite historical story events or change the event-ledger head.

A third axis—**exchange schema**—governs packets and sidecars outside the immutable event envelope. Rev0159 advanced new turn issuance to `lacuna.turn-request.v4`, `lacuna.turn-grant.v2`, and source protocol `lacuna.turn-request-source.v3`, while continuing to validate historical request v2/v3 and grant v1 objects without rewriting them. It also added checkpoint request, card, candidate, judgment, compression, proposal, verifier, review, commit-receipt, and stateless dispatch v1 contracts. Rev0160 adds the managed sidecar layer `lacuna.checkpoint-run.v1`, `lacuna.checkpoint-run-agent-dispatch.v1`, and `lacuna.checkpoint-invocation-receipt.v1`. Rev0161–rev0162 add single-block and replicated scenario exchange contracts. Rev0163 adds `lacuna.checkpoint-narrator-capsule.v1`, extends scenario driver/return contracts with continuation-mode, managed-checkpoint, and capsule-linkage fields, and strengthens scenario-capsule v1 so every checkpoint has a following observable script turn. Rev0164 adds `lacuna.checkpoint-continuation-dispatch.v1`, `lacuna.public-history.v1`, and `lacuna.public-history-view.v1`. Rev0165 advances the continuation/public-history family to v2 so an explicit ordered run list is distinguishable from a checkpoint-bound complete durable-turn census. It also advances scenario run, cell-driver, report, bundle block-seal, and bundle report custody to v2 and adds `lacuna.scenario-contamination-plan.v1` plus `lacuna.scenario-contamination-scan.v1`; database schema 8 and event schema 1 remain unchanged. Exchange evolution does not imply a database migration.

## Current exchange lineage

The current managed checkpoint path composes existing exchange objects rather than replacing them:

```text
turn request v4 / grant v2 / source v3
        ↓
checkpoint request v1
        ↓
checkpoint task card v1 + role output v1 objects
        ↓
checkpoint proposal / verifier / review / commit receipt v1

managed host custody around that chain:
checkpoint run v1
checkpoint run agent dispatch v1
checkpoint invocation receipt v1
        ↓ after committed audit, when requested
checkpoint narrator capsule v1
        ↓ exact fresh next turn
checkpoint continuation dispatch v2
        ↙ parent/auditor custody        ↘ worker least-context projection
public history v2                 public history view v2
  ├─ explicit-run-list / completeness not claimed
  └─ complete-before-checkpoint / ledger census authenticated

Historical continuation/public-history v1 schemas remain validation contracts for rev0164 artifacts.

scenario custody:
scenario run v2 → contamination plan v1 → cell driver v2 / cell return v1
        → contamination scan v1 → blind rating packet v1 → scenario report v2
replicated custody:
bundle block seal v2 binds child scan → bundle report v2 exports condition-mapped findings
```

The managed manifest is strict to the creating Lacuna project version. It has no run migration or relocation layer. Historical turn requests and the lower-level checkpoint objects retain their own validation rules; a managed run does not rewrite them merely because its pointer or invocation metadata advances.

## Canonical database lineage

```text
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8
```

The current runtime can migrate a coherent schema-1 through schema-7 cube forward to schema 8 in one explicit command. Each step has a deterministic statement tuple and SHA-256 migration digest recorded in `schema_migrations`.

## Historical schema-6 collision

Two sibling rev0151 development branches independently claimed database schema number 6:

- the canonical fair-play branch used 5→6 for `fair_play_seals`;
- an experimental sibling used 5→6 for event-backed particle update tables.

The canonical rev0151 artifact delivered to the user was the fair-play branch. Its fresh schema also retained two empty dormant particle tables for compatibility, while its 5→6 migration did not create those tables. That produced two official schema-6 physical variants:

1. **fresh schema 6:** fair-play tables plus empty dormant particle tables without `world_status`;
2. **migrated schema 6:** fair-play tables and no particle tables.

Rev0152 resolved the collision by preserving the official fair-play 5→6 digest and creating a new canonical 6→7 particle migration. Rev0153 preserves that lineage unchanged.

## The 6→7 migration

The migration accepts either official schema-6 shape when particle tables are absent or empty. It then:

1. drops any empty dormant particle tables;
2. creates canonical `particle_updates` and `particle_update_members` tables;
3. records historical `world_status` for every assessed member;
4. adds a unique evidence-factor index so one assertion cannot be multiplied twice;
5. records the 6→7 migration digest; and
6. advances metadata and `PRAGMA user_version` only after full shape validation.

The ledger head is checked before and after migration and must remain byte-identical.

### Refusal on nonempty dormant rows

Schema-6 particle rows in the canonical parent lineage have no official immutable event owner. Silently dropping them would destroy forensic state; silently adopting them would pretend provenance that does not exist.

Migration therefore performs a schema-6-only preflight count. Any nonempty `particle_updates` or `particle_update_members` table produces:

```text
migration-preflight-failed
  code: unowned-particle-projection-rows
```

The operator must export those rows, inspect their origin, and use an explicit forensic repair before retrying.

This refusal must **not** run for schema 7. Schema-7 particle rows are canonical event-owned projections. Rev0153 includes a migration regression proving that a real schema-7 cube with particle history advances to schema 8 intact.

## The 7→8 migration

Rev0153 adds factor-ledger reconciliation custody with one deterministic additive migration. It creates:

```text
particle_reconciliations
particle_reconciliation_factors
particle_reconciliation_members
```

and their named indexes.

The tables record:

- one reconciliation identity, method, review digest/head-derived custody, boundary, baseline/current/posterior bank digests, factor-set digest, statistics, reason, and origin sequence;
- ordered included/excluded factor dispositions and evidence-ending custody; and
- complete ordered per-world baseline/current/posterior replay arithmetic and fingerprints.

The 7→8 migration does not rewrite particle updates, events, changesets, or world weights. Existing projection state is preserved; new reconciliation projections begin empty. The event-ledger head remains unchanged.

## Migration records and shape validation

Every migration step records:

- source and target database versions;
- deterministic migration statement digest;
- application time; and
- exact step identity.

After migration, Lacuna validates the complete expected physical shape, including:

- table names and columns;
- declared types, nullability, and primary keys;
- foreign keys;
- named indexes, uniqueness, partiality, and columns;
- metadata/`PRAGMA user_version` agreement;
- SQLite integrity and foreign-key integrity; and
- unchanged story event-ledger head.

Defaults are excluded from shape equivalence where an old migration needed a compatibility default but newly initialized cubes always write the field explicitly.

## Unsupported sibling import

The experimental particle rev0151 sibling remains design prior art, not an alternative canonical parent. A cube containing sibling-only particle events or rows should be exported and migrated through a purpose-built importer rather than relabelled as the fair-play schema-6 lineage.

This prevents a version-number collision from becoming silent history rewriting.

## Host procedure

```bash
./lacuna status CUBE
./lacuna verify CUBE
./lacuna migrate CUBE
./lacuna verify CUBE
```

Normal `Cube.open` refuses an older database with `database-migration-required`. Migration is explicit so the operator can retain pre-migration custody and inspect any refusal.

## Nonclaims

A passing migration proves that the runtime applied its recorded structural steps and preserved the checked ledger head. It does not prove:

- that every historical event was truthful;
- that the host never forked or replaced the database before inspection;
- that an unofficial branch was semantically equivalent;
- that projection data outside immutable event custody should be trusted;
- that floating-point calculations are bit-identical across arbitrary runtimes; or
- that future schema versions can be inferred from the current one.
