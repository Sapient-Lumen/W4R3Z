# Architecture — rev0151

## Architectural thesis

Lacuna is a deterministic epistemic custody kernel. It should preserve enough structure for an adaptive planner to change its mind without rewriting experienced facts, while refusing to infer that a coherent story is automatically a true, fair, or causal one.

Rev0151 adds a complementary primitive: selected hidden values can be cryptographically precommitted while remaining absent from the cube until reveal.

## Boundary diagram

```text
                            external custody boundary

  player/human host     model provider       secret opening file      witness/log
         |                    |                      |                       |
         | exact input        | proposal JSON        | payload + nonce       | receipt digest
         v                    v                      |                       |
  +-------------------------------------------------------------------------+
  |                         host / adapter                                   |
  |  campaign selection | packet assembly | seal administration | retention |
  +-------------------------------------------------------------------------+
                    | typed CLI / Python calls
                    v
  +-------------------------------------------------------------------------+
  |                           LACUNA KERNEL                                  |
  |                                                                         |
  | immutable events + change receipts                                      |
  | claims | assertions | sources | worlds | assignments | constraints      |
  | commitments | consequences | repairs | questions | fair-play digests    |
  |                                                                         |
  | perspective projection      planner projection      verification/replay  |
  +-------------------------------------------------------------------------+
                    |
                    v
           SQLite event ledger + replayable projections
```

The opening file is intentionally not below the kernel boundary before reveal. The witness/log is optional and external.

## Storage layers

### Immutable event ledger

Every accepted mutation produces one or more sequence-ordered events with:

- event identity and type;
- actor;
- recorded time;
- exact canonical payload;
- previous event hash;
- event hash;
- atomic change-set identity.

Change receipts bind expected, before, and after heads. The chain is locally tamper-evident under the current verifier; it is not a signature or public transparency service.

### Replayable projections

SQLite projection tables make current state queryable. They are disposable in the architectural sense: a passing ledger-only verification can replay events to rebuild them.

Schema 6 projections include:

- agents and sources;
- neutral claims and scoped assertions;
- claim relations and cardinality constraints;
- candidate worlds and assignment lineage;
- commitment transitions;
- evidence and consequence links;
- consequence repair lineage;
- questions;
- fair-play seals.

Two old particle-update tables remain only for database-shape compatibility. No immutable event type owns them. Any rows are a verification error and rebuild removes them.

### Campaign library

The library maps human campaign slugs to cube directories and tracks one selected campaign. It is convenience metadata, not semantic story custody. Ordinary cube commands resolve either a direct cube or the active campaign in a library.

## Epistemic model

### Claims are content, not truth

A claim identifies proposition content. Assertions say who takes what stance, from which source and perspective, with what basis, standing, confidence, visibility, and interval.

### Candidate worlds are partial hypotheses

World assignments are explicit partial valuations. Missing is not false. Pairwise and cardinality constraints can refuse incompatible explicit combinations but do not manufacture closure.

World selection and weight are planning policy. They are not canonization or certified probability.

### Commitment governs revision

Assignment commitment is distinct from truth and confidence. Revision requires a reviewed successor lineage; hard assignment commitment blocks ordinary in-place truth change.

### Consequences record authored dependence

A consequence link says an assignment is treated as a premise for another identified record. It is authored custody, not proof of physical causality. Reviewed repair can replace one active link while preserving predecessor and successor history.

### Fair-play seals bind external openings

A seal projection stores:

```text
seal identity
scheme + salted digest
label + purpose
visibility + audience
optional privileged provenance source
origin sequence
terminal reveal or void state
```

Before reveal, no nonce or payload exists in the event ledger or projection. After reveal, the exact opening is event-backed and digest-verifiable.

A seal is not an assertion or assignment. This avoids automatic semantic elevation of a design artifact.

## Fair-play protocol data flow

### Preparation

```text
payload JSON
   + cube_id
   + seal_id
   + random 256-bit nonce
          |
          v
canonical commitment core -> SHA-256 -> opening bundle
                                      (kept outside cube)
```

### Creation

```text
opening bundle --parse/self-check--> digest + metadata only
                                      |
                                      v
                              precommitment.sealed event
                                      |
                                      v
                               fair_play_seals row
                                      |
                                      v
                        immutable receipt core + digest
```

### Reveal

```text
opening bundle + recorded digest
           |
           v
recompute / constant-time compare
           |
           v
precommitment.revealed event -> revealed projection -> receipt with opening
```

Create and reveal must be separate committed change-sets.

## Receipt structure

`lacuna.fair-play-seal-receipt.v1` separates four concerns:

- `receipt_core`: immutable origin metadata;
- `receipt_sha256`: stable digest over the core;
- `seal`: convenient current lifecycle view;
- `opening` or `resolution`: terminal state when applicable.

The core contains only:

- cube ID;
- immutable seal fields;
- origin event envelope and origin change head.

It excludes `current_head`, live status, reveal sequence, void sequence, opening, and resolution. Tests assert stability across reveal.

## Access architecture

### Perspective context

A named perspective receives only records visible to it. For fair-play seals:

- public seals are visible;
- restricted seals are visible only to named audience agents;
- privileged source linkage is removed;
- hidden source dependencies do not appear in perspective explanations.

### Planner context

Planner context may include all seal records and provenance linkage. The presence of a seal still does not disclose the opening before reveal.

### Model turn authority

Audience turn grants expose only audience-safe operations. Director grants expose ordinary hidden-world authoring operations but subtract three host-custody operations:

```text
seal_precommitment
reveal_precommitment
void_precommitment
```

The direct host/CLI API remains the administrative entrance. This is an explicit authority lattice rather than a single boolean “privileged” flag.

## Verification architecture

Full verification checks:

1. database shape, schema version, and migration custody;
2. SQLite integrity and foreign keys;
3. event sequence, type, schema, hash, and previous hash;
4. change receipt contiguity and head binding;
5. global projection invariants;
6. assignment/revision/commitment consistency;
7. relation/cardinality/consequence/repair consistency;
8. seal origin, lifecycle, digest, event equality, and phase separation;
9. absence of unsupported particle projection rows.

Ledger-only verification ignores disposable projection foreign-key failures so a valid event history can rebuild corrupted projections. It never ignores malformed or mutated events.

## Exchange contracts

Rev0151 ships strict Draft 2020-12 JSON Schemas for:

- campaign and library metadata;
- direct change-sets;
- source-bound turn requests and proposals;
- seal openings;
- fair-play seal receipts.

Runtime registries and exchange schemas are compared in tests. Host-only seal operations appear in direct change-sets but are deliberately absent from turn proposals.

## Executable boundary

The bundled `./lacuna` entrance is a POSIX wrapper over `python3 -S -m lacuna.cli` with the repository `src/` directory explicitly supplied. Because the runtime has no third-party dependencies, disabling normal site initialization prevents machine-local packages and `sitecustomize` hooks from silently becoming part of Lacuna’s trusted computing base. This does not sandbox Python, authenticate callers, or constrain direct library embeddings; it makes the shipped subprocess entrance narrower and reproducible.

## Model-host pattern

Lacuna does not invoke an LLM. A host:

1. creates a source-bound turn packet;
2. sends that packet to any model or human;
3. receives one typed proposal;
4. commits it atomically;
5. displays narration only from the accepted receipt;
6. returns the latest audience state and head beside the prose.

Seal lifecycle is a separate administrative channel and should not share the narrator model’s prompt or tool grant.

## Schema evolution

Database schema 6 adds `fair_play_seals` through explicit migration 5→6. Migration:

- is requested separately rather than performed on open;
- checks coherent source shape;
- records a digest-identified migration row;
- preserves the event count and head;
- participates in ordered migration from schema 1 through 5.

## Deliberately external

The architecture does not absorb:

- model API clients or credentials;
- transcript bodies;
- prose entailment checking;
- dramatic scoring or world generation;
- particle posterior computation;
- fair-play quality metrics;
- external signatures, timestamps, witnesses, or transparency logs;
- game-engine physical simulation;
- authentication and network transport;
- self-modification or release machinery.

Those systems can use Lacuna, but none should silently become a second source of canon.
