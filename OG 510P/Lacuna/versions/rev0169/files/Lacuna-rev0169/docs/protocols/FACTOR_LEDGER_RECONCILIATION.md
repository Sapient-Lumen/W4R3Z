# Factor-ledger reconciliation

## Purpose

A particle update is an immutable record of what a planner did with one evidence assertion at one ledger head. The current particle weights are a derived planning surface. Those two facts create a necessary asymmetry:

- history must not be rewritten when evidence is withdrawn; and
- current weights must not continue to masquerade as supported by withdrawn evidence.

Factor-ledger reconciliation repairs the derived distribution while preserving every original update. It is reason maintenance for planning weights, not event rollback.

## Governing rule

> Rebuild the current distribution from the immutable prior of the latest structurally coherent factor epoch, multiply every still-authorized factor exactly once, retain every unauthorized factor as excluded custody, and append a separate reconciliation event.

A reconciliation changes weights only. It does not change what any world says, whether a world is live, which assertion ended, or what happened during the campaign.

## Vocabulary

**Factor** — one `particle.updated` record whose `evidence_assertion_id` supplied a complete likelihood vector over the then-current eligible population.

**Factor epoch** — the interval after the most recent structural mutation of the eligible particle population or its authored prior. Its boundary is the latest event of one of these types:

```text
world.created
world.assigned
world.revised
world.commitment_raised
world.weight_set
world.status_set
```

These events can change membership, explicit valuation, custody, status, or authored prior weight. A likelihood assessed before such a change is not silently replayed across it.

**Baseline** — the exact prior bank recorded by the first particle update after the epoch boundary. It is reconstructed from that update's immutable member receipts rather than inferred from current weights.

**Included factor** — a factor in the current epoch whose evidence assertion is active at the reconciliation head.

**Excluded factor** — a factor in the current epoch whose evidence assertion ended before the reconciliation. The factor and its original effect remain in history; its disposition is recorded as `excluded` with reason `evidence-superseded`.

**Reconciliation** — one immutable `particle.reconciled` event and its replayable projection. It identifies the baseline, structural boundary, complete factor selection, old current bank, calculated posterior bank, per-world arithmetic, and review authorization.

## Why an epoch is necessary

Likelihoods are assessed against a particular complete population and a particular custody fingerprint for every member. Replaying them after a world is added, removed from eligibility, reassigned, revised, recommitted, or manually reweighted would answer a different question with stale assessments.

Lacuna therefore chooses a conservative boundary. Structural mutation retires the previous factor epoch. Its factors remain queryable but no longer create current reconciliation debt. New evidence updates after the boundary establish a new baseline.

This rule deliberately prefers an explicit new assessment to a clever guess that an old likelihood remains applicable.

## Review-first flow

```text
current ledger head
      +
latest structural boundary
      +
first update's immutable prior snapshot
      +
all later factor receipts in the epoch
      +
current active/superseded state of each evidence assertion
      │
      ▼
complete deterministic review
      │
      ├─ blockers
      ├─ included factor set
      ├─ excluded factor set
      ├─ log-space posterior
      └─ expected reconciliation digest
      │
      ▼
reconcile_particle_bank
      │
      ▼
particle.reconciled + updated world weights + immutable custody
```

`particle_reconciliation_review()` is bound to:

- cube identity;
- one ledger head;
- epoch boundary;
- baseline update and bank digest;
- current bank digest;
- ordered included and excluded factor summaries;
- complete calculated member result; and
- every blocker.

Any separately committed intervening event changes the head and makes the digest stale. Within an atomic turn or change set, the review is rebound to the change set's base head while relevant earlier operations in the same transaction still alter the calculated state and cause refusal when incompatible.

## Replay arithmetic

For world \(i\), baseline probability \(p_i\), and included factors \(L_{ki}\):

\[
\ell_i = \log p_i + \sum_k \log L_{ki}
\]

Worlds with zero baseline mass or any zero included likelihood have zero posterior mass. Positive scores are normalized with a max-shifted log-sum-exp calculation:

\[
q_i = \frac{\exp(\ell_i - m)}{\sum_j \exp(\ell_j - m)},
\qquad m = \max_j \ell_j
\]

This prevents a long product of small positive likelihoods from becoming zero merely because intermediate IEEE-754 multiplication underflowed. The runtime uses only the Python standard library; the algorithm is the same max-shift principle documented by SciPy's `logsumexp` operation.

The stored reconciliation member carries:

- current raw weight and probability before repair;
- baseline raw weight and probability;
- sum of included log-likelihood terms;
- the first factor that explicitly extinguished the world, when any;
- posterior probability; and
- valuation and custody fingerprints.

No `NaN`, positive infinity, or negative infinity is emitted into event JSON or projections.

## Reconciliation is not rollback

The original `particle.updated` event remains true as custody: it records the evidence available and arithmetic authorized at that time. Reconciliation does not delete it, alter its projection, or pretend it never influenced planning.

Instead, `particle.reconciled` says that at a later head:

- these factors remain authorized;
- these factors are excluded because their evidence ended;
- this immutable baseline was replayed; and
- this is the new derived distribution.

The current bank reports each historical factor as one of:

- `epoch-retired`;
- `active-in-current-epoch`;
- `reconciliation-required`; or
- `reconciled-excluded`.

A superseded factor creates `reweighting_debt` only while it belongs to the current epoch and has not been explicitly excluded by a later reconciliation.

## Refusals

Reconciliation is refused when, among other conditions:

- no particle update exists after the latest structural boundary;
- the baseline snapshot does not reproduce the first update's prior-bank digest;
- current membership differs from baseline membership;
- current status, valuation fingerprint, or custody fingerprint differs from baseline;
- an included factor does not cover exactly the baseline population;
- an included factor's recorded member custody differs from the baseline;
- replay would assign zero mass to every world;
- the review digest is malformed or stale;
- the requested reconciliation ID already exists; or
- the same factor set and posterior are already reconciled.

The final rule prevents repeated no-op custody events after a successful repair. A first reconciliation with no total-variation change is still permitted: it may establish log-space replay custody or prove that an active ledger reproduces the current bank.

## Entrances

### Human CLI

```bash
./lacuna particle-bank CUBE
./lacuna particle-reconciliation-review CUBE > /tmp/reconciliation.json
./lacuna particle-reconcile CUBE \
  --reconciliation-id prc.factor-audit.001 \
  --expected-reconciliation-sha256 DIGEST_FROM_REVIEW \
  --reason "Replay active factors and exclude withdrawn evidence."
./lacuna particle-reconciliations CUBE
```

The review is useful even when blocked: it identifies the boundary, selected factors, projected result, and exact refusal reasons.

### Direct Python

```python
review = cube.particle_reconciliation_review()
if review["ready"]:
    cube.apply_operations(
        actor_id="director",
        operations=[
            {
                "op": "reconcile_particle_bank",
                "reconciliation_id": "prc.factor-audit.001",
                "expected_reconciliation_sha256": review[
                    "expected_reconciliation_sha256"
                ],
                "reason": "Repair the current factor interpretation.",
            }
        ],
    )
```

### Director turn

An unscoped director packet includes the complete reconciliation review and recent reconciliation custody. Its grant may authorize `reconcile_particle_bank`.

A world-scoped director packet omits both and refuses the operation. Reconciliation governs the complete denominator; it cannot be authorized from one branch-local view.

### Audience context

Perspective context contains neither the review nor reconciliation history. IDs, factor dispositions, counts, likelihood arithmetic, and hidden-world membership are omitted structurally. A perspective explanation of a reconciliation is refused.

## Event and database custody

Rev0153 retains event schema 1 and adds event type `particle.reconciled`. Database schema 8 adds:

```text
particle_reconciliations
particle_reconciliation_factors
particle_reconciliation_members
```

The factor table preserves included and excluded dispositions. The member table preserves complete per-world replay arithmetic. Current world weights remain a projection updated by the reconciliation event and can be rebuilt from the event ledger.

`verify` independently reconstructs:

- origin event and change-set binding;
- latest structural boundary at the event sequence;
- active versus ended evidence at the event sequence;
- ordered factor selection and factor-set digest;
- baseline and current bank digests;
- log-space posterior arithmetic;
- distribution statistics and total variation;
- per-world member values and extinguishing factor;
- review digest and base head; and
- event/projection completeness.

Projection tampering produces structured audit failures. `rebuild-projections` discards derived reconciliation rows and world weights and deterministically replays them from immutable events.

## Separation of powers

Reconciliation may:

- repair the current arithmetic interpretation of an immutable factor ledger;
- exclude factors whose evidence has ended;
- recover positive posterior mass lost only to sequential floating-point underflow;
- update planning weights atomically; and
- produce inspectable reason-maintenance custody.

It may not:

- reactivate an assertion;
- delete or edit a particle update;
- change a likelihood assessment;
- infer that two evidence assertions are independent;
- move a factor across a structural epoch;
- create, prune, merge, fork, resample, or select worlds;
- change assignments, commitments, or consequences;
- certify a causal explanation or player agency;
- disclose hidden state; or
- make a candidate world canon.

## Research lineage

The design combines four established ideas without claiming identity with any of them:

- Jon Doyle's truth-maintenance work emphasizes retaining reasons and revising derived beliefs when supporting assumptions change: [A Truth Maintenance System, MIT AI Memo 521](https://dspace.mit.edu/handle/1721.1/5733).
- Event sourcing treats current state as a replayable projection over immutable events and supports correction through new events rather than destructive edits: [Martin Fowler, Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html) and [Retroactive Event](https://martinfowler.com/eaaDev/RetroactiveEvent.html).
- Sequential Monte Carlo provides the weighted-hypothesis vocabulary and concentration diagnostics, while warning that ESS is only a surrogate when the particle approximation itself is poor: [Doucet and Johansen, A Tutorial on Particle Filtering and Smoothing](https://www.stats.ox.ac.uk/~doucet/doucet_johansen_tutorialPF2011.pdf).
- Max-shifted log-sum-exp is the standard numerical pattern for stable normalization of log weights: [SciPy `logsumexp` documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.logsumexp.html).

Lacuna's specific contribution is to place those ideas behind a typed, head-bound, visibility-safe narrative custody protocol.

## Nonclaims

A passing reconciliation proves that Lacuna replayed the recorded authorized factors over the recorded baseline according to its stated arithmetic. It does not prove:

- that likelihoods are calibrated probabilities;
- that evidence factors are conditionally independent;
- that the baseline prior was wise;
- that the candidate population is complete or diverse;
- that a zero likelihood was semantically justified;
- that the highest-weight world is true;
- that player actions had causal rather than interpretive agency;
- that the story is coherent, fair, interesting, or good; or
- that the host has not forked, replaced, or selectively presented the cube.
