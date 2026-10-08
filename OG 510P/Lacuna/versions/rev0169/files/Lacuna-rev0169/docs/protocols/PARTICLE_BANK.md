# Governed particle bank

## Purpose

Lacuna keeps more than one hidden-world hypothesis alive. Rev0153 provides a deterministic **particle-bank projection**, evidence-bound updates, and governed factor-ledger reconciliation across the complete live population without selecting, pruning, merging, resampling, or canonizing a world.

The particle bank is not a probability oracle. Its weights and likelihoods are authored planning quantities. The protocol borrows the mechanics of sequential importance reweighting—normalization, likelihood multiplication, effective sample size, entropy, and immutable update receipts—while refusing the statistical claims that would require a calibrated generative model.

The governing distinction is:

> A hypothesis may become more useful for planning without becoming more true in the ledger.

## Membership

The bank contains every world whose status is `live` or `selected`, ordered by `world_id`.

`pruned` and `archived` worlds remain in historical custody but are not members of the current bank. A particle update never changes status. Pruning, archiving, selection, forking, and eventual canonization remain explicit independent operations.

Each member exposes:

- `world_id`, label, and historical status;
- stored `raw_weight`;
- normalized `probability`, when total mass is positive;
- active assignment count;
- `valuation_sha256`; and
- `custody_sha256`.

### Valuation fingerprint

`valuation_sha256` hashes only explicit active assignment propositions:

```text
claim_id | truth | timeline_id | valid_from | valid_to
```

It deliberately ignores assignment identity, confidence, commitment, provenance, and lineage. Two worlds with the same explicit valuation therefore land in one diagnostic equivalence group.

This is a narrow statement. It does not prove that the complete worlds are identical. Unrepresented geography, motives, causal structure, character state, host simulation state, or prose-only assumptions may differ.

### Custody fingerprint

`custody_sha256` also includes assignment identity, commitment, commitment basis and source, confidence, supporting assertion, inheritance, and revision lineage. It is designed to stale a review when the recorded planning state changes even if the explicit truth valuation does not.

### Bank digest

`bank_sha256` binds the complete current population:

```text
policy
for every live/selected world:
  world_id
  status
  raw_weight
  valuation_sha256
  custody_sha256
```

The digest excludes labels and prose rationale because they do not change the assessed hypothesis surface and are immutable in the current kernel. It includes raw weight and status because both affect the prior population.

## Review before mutation

Request a review for one active evidence assertion:

```bash
./lacuna particle-update-review CUBE ast.red-dust
```

The review returns:

- the active evidence assertion and claim;
- current ledger head;
- complete particle bank;
- `expected_bank_sha256`; and
- the exact world IDs that must be assessed.

A proposer must assess every live or selected world exactly once. Missing worlds, extra worlds, duplicate worlds, stale bank digests, inactive evidence, an empty bank, zero total prior mass, an all-zero posterior, or reuse of an already-applied evidence assertion are refused before any event is appended.

## Update equation

For world `i`, with normalized prior `p_i` and authored likelihood `l_i`:

```text
u_i = p_i × l_i
Z   = Σ u_i
q_i = u_i / Z
```

The committed world weight becomes `q_i`. All worlds retain their status and assignments.

The `particle.updated` event records for every member:

- historical status;
- prior raw weight and normalized prior;
- authored likelihood and optional rationale;
- unnormalized weight;
- posterior probability;
- valuation fingerprint; and
- custody fingerprint.

The event also records the prior and posterior bank digests, normalization constant, effective sample size, entropy, information gain, zero-likelihood count, equivalent-valuation divergence groups, reason, evidence assertion, and origin event/change custody.

## Evidence-factor custody

### Single use

One `evidence_assertion_id` may authorize at most one particle update.

This is intentionally stricter than “multiply whenever convenient.” Applying the same evidence factor twice silently exaggerates its influence. Lacuna therefore centralizes an active-unused assertion check at both the review and mutation entrances, keeps a unique projection constraint, and emits one refusal code:

```text
particle-evidence-already-applied
```

Two uses inside one atomic change-set roll back together, so the first attempted multiplication leaves no trace. A corrected observation should be represented by superseding the old assertion and recording a new assertion. Removing the old factor from current support requires the separately reviewed factor-ledger reconciliation protocol; ordinary reweighting never rewrites prior factors.

### Supersession debt and factor status

An evidence assertion can be superseded after it has already contributed to weights. Lacuna does not retroactively rewrite the event or silently unapply the factor. Instead the current particle-bank projection exposes:

- `applied_factors`;
- each factor's active or superseded evidence status;
- each factor's ledger status and resolution custody;
- `reweighting_debt_count`; and
- `reweighting_debt` entries identifying current-epoch updates whose evidence is no longer active and has not been reconciled.

Ledger status is one of:

- `active-in-current-epoch`;
- `reconciliation-required`;
- `reconciled-excluded`; or
- `epoch-retired`.

This is a debt signal, not corruption. The historical update remains valid custody of what the planner did at that time. [`FACTOR_LEDGER_RECONCILIATION.md`](FACTOR_LEDGER_RECONCILIATION.md) defines the separate review and event that rebuild current weights from the immutable epoch baseline.

## Diagnostics, not verdicts

### Effective sample size

```text
ESS = 1 / Σ p_i²
```

ESS describes weight concentration. It does not say how many genuinely different stories remain, because separate particles may encode the same explicit valuation or differ in unrepresented state.

### Entropy

Lacuna reports Shannon entropy in nats and normalized entropy for the current bank. These describe the weight vector, not narrative diversity, mystery quality, or agency.

### Information gain

The update receipt reports `KL(q || p)` in nats. This is a mathematical difference between two authored weight vectors. It is not proof that the evidence was informative under a calibrated statistical model.

### Equivalent-valuation divergence

If worlds with the same valuation fingerprint receive different likelihoods, Lacuna permits the update but surfaces `valuation_likelihood_divergence_groups`. The difference may be legitimate because the worlds differ outside the fingerprint. It may also reveal that the assessor is relying on hidden or unstated distinctions. The kernel records the seam rather than guessing.

### Reweighting debt

A bank with superseded factors may still be internally normalized. Normalization does not erase epistemic debt. Hosts should display the debt and avoid calling the resulting vector a current posterior.

## Separation of powers

A particle update may:

- normalize current raw weights;
- apply one complete likelihood vector;
- record immutable evidence-update custody;
- change weights atomically; and
- expose concentration, equivalence, and supersession diagnostics.

It may not:

- create or delete worlds;
- select, prune, archive, merge, fork, or resample worlds;
- add or revise assignments;
- anchor a claim;
- infer missing truth;
- certify a culprit, cause, motive, or ending;
- reveal hidden state to an audience;
- claim that a player action caused downstream divergence; or
- silently retract or replay earlier evidence factors.

Factor reconciliation is a distinct operation. It may replay currently authorized factors and exclude ended factors, but cannot alter likelihoods, author a new prior, or move factors across a structural epoch.

Those boundaries are intentional. Reweighting, proposal, resampling, pruning, selection, commitment, disclosure, and canonization are different acts and require different review surfaces.

## Entrances

### Human CLI

```bash
./lacuna particle-bank CUBE
./lacuna particle-update-review CUBE ast.red-dust > review.json
./lacuna particle-update CUBE ast.red-dust \
  --expected-bank-sha256 DIGEST \
  --assessment world.river=0.8 \
  --assessment world.road=0.2 \
  --reason "The threshold dust favors the river route."
./lacuna particle-updates CUBE

# After applied evidence ends:
./lacuna particle-reconciliation-review CUBE > reconciliation.json
./lacuna particle-reconcile CUBE \
  --expected-reconciliation-sha256 DIGEST \
  --reason "Replay active factors and exclude withdrawn evidence."
./lacuna particle-reconciliations CUBE
```

The compact CLI assessment syntax supplies a likelihood only. Use a typed change set or turn proposal when per-world rationales are required.

### Direct Python

```python
review = cube.particle_update_review("ast.red-dust")
receipt = cube.apply_operations(
    actor_id="director",
    operations=[
        {
            "op": "update_particle_bank",
            "evidence_assertion_id": "ast.red-dust",
            "expected_bank_sha256": review["expected_bank_sha256"],
            "assessments": [
                {"world_id": "world.river", "likelihood": 0.8},
                {"world_id": "world.road", "likelihood": 0.2},
            ],
            "reason": "Redistribute planning attention after recorded evidence.",
        }
    ],
)
```

### Director turn

An unscoped director packet contains the complete privileged bank, current reconciliation review, and recent repair custody. It may receive `update_particle_bank` and `reconcile_particle_bank` in its least-authority grant. A world-scoped director packet omits these global surfaces and cannot mutate them: a filtered population would create a false normalization or replay surface.

The narration source and particle update or reconciliation can commit in one atomic turn. Reviewed receipts are rebound to the turn request's resulting head without changing their independently computed population/factor calculations.

### Audience context

Audience context contains neither the bank, update receipts, reconciliation review, nor reconciliation custody. Their IDs, counts, rationales, fingerprints, factor dispositions, diagnostics, and debt are omitted structurally. A perspective explanation of a particle update or reconciliation is refused.

## Replay and audit

Database schema 8 owns `particle_updates`, `particle_update_members`, `particle_reconciliations`, `particle_reconciliation_factors`, and `particle_reconciliation_members`. Event schema remains 1 with additive event types `particle.updated` and `particle.reconciled`.

`verify` checks:

- origin event type and identity;
- event/projection parity;
- evidence existence;
- complete ordered member custody;
- historical status and digest formats;
- finite numeric values and allowed ranges;
- prior/posterior normalization;
- update equation;
- ESS, entropy, and information-gain recomputation;
- zero-count and divergence diagnostics;
- reconstructible prior and posterior bank digests;
- particle events missing their projections; and
- physical schema shape, including the single-use evidence index.

Malformed numeric projection values produce structured audit failures rather than exceptions. Reconciliation verification additionally reconstructs the event-time structural boundary, active/ended factor selection, baseline and current bank digests, factor-set and review digests, max-shifted log replay, per-world results, and total-variation/statistic fields. `rebuild-projections` deletes derived particle tables and reconstructs them from immutable events.

## Schema lineage

Two rev0151 sibling branches independently used database schema number 6: the canonical parent branch for fair-play seals and an experimental sibling for particle updates. Rev0152 retained the fair-play branch as parent and moved the unified physical shape to schema 7. Rev0153 adds reconciliation custody through a normal additive 7→8 migration.

The historical 6→7 migration:

1. preserves the official 5→6 fair-play migration digest;
2. refuses nonempty event-unowned particle projection rows rather than deleting them;
3. replaces either empty dormant schema-6 particle shape—or no particle tables at all—with canonical event-owned tables;
4. adds historical `world_status` and single-use evidence-factor custody; and
5. preserves the story event-ledger head.

The 7→8 migration preserves all event-owned particle update rows, adds reconciliation tables and indexes, records its deterministic digest, and leaves the event-ledger head unchanged. The schema-6 unowned-row preflight is not applied to legitimate schema-7 projections.

See [`SCHEMA_LINEAGE.md`](SCHEMA_LINEAGE.md).

## Deliberate omissions

Rev0153 does not implement:

- automatic resampling or ancestry;
- particle birth proposals;
- diversity-preserving clustering or minority reserves;
- semantic correction/replacement of an authored likelihood vector;
- calibration of authored likelihoods;
- automatic evidence-dependence checks;
- log-space ordinary updates between reconciliations or an exact cross-language numeric wire standard;
- causal-agency measurement;
- counterfactual rollout validation; or
- a winning-world selector.

The next safe step is not “pick the maximum.” It is explicit factor-dependence/replacement custody and then a proposal/ancestry protocol for adding or resampling candidates while preserving minority explanations and making particle impoverishment inspectable.
