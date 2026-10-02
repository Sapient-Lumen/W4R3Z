# ADR 0171: Qualify load-aware sync admission topology

Status: accepted for topology and counterbalanced policy phase order, 2026-08-25.

## Context

ADR 0170 froze a conservative adaptive selector at the deterministic Agent boundary. Gate 4 still
needed genuine provider evidence that a later overlapping pull observes work already admitted by an
earlier pull. The first experiment must distinguish route placement from throughput: a small fixture
can prove which authenticated carrier was selected without pretending to measure useful bandwidth,
fairness, or large-object convergence.

## Decision

The Sandwurm scenario `sync-tree-route-balance` runs two simultaneous source-linked IoTox guests with
one protected primary and two reciprocally authenticated bulk routes per guest. Each bulk member has
eight signed work slots. The publisher creates four distinct signed namespaces over one deterministic
8,192-byte tree, producing one 8,259-byte treepack artifact per namespace.

One subscriber process performs two serialized policy phases. The first accepted cells run fixed
then adaptive; a second independently booted pair on each carrier runs adaptive then fixed. Within
each cell the first policy uses the ordinary sync-enablement start and the second follows a clean
Agent restart over the same durable state. Each policy phase performs the same experiment:

1. Start the first pull and wait until its two immutable objects are assigned to one auxiliary route
   with positive admitted work. Start the second pull while that route remains eligible.
2. Under `fixed`, require both jobs to name the same auxiliary carrier. Under `adaptive`, require the
   second job to name the other idle auxiliary carrier.
3. Verify and activate both revisions, then require empty staging and zero route work before changing
   policy or entering the protected-Ratox tail.

Each phase requires exactly two selection decisions. Every job must request, admit, and commit exactly
two objects; all four exact signed HEADs must activate; every staging directory and route-work counter
must return to zero. A bounded idempotent HEAD retry remains available to make a lost control response
explicit, and the receipt records its use. The accepted direct-UDP and forced-TCP cells required zero
retries. After both phases, the protected primary must still complete 40 ordered Ratox samples below
250 ms.

Raw and compact verification bind phase order, carrier equality/inequality, policy decision counts, activation,
artifact size, retry bounds, authenticated route population, Ratox/resource evidence, native carrier
class, and the exact source-linked binary. Fixed-first direct UDP `pair.ul1pdq7m` and forced TCP
`pair.pz9aapaj` pass; adaptive-first direct UDP `pair.hhmma27l` and forced TCP `pair.jn5aqbr6` pass
against the same exact binary.

## Consequences

- IoTox now has genuine evidence that current coordinator load reaches a later admission decision and
  changes placement under the adaptive policy on both native carrier classes.
- Fixed remains the default. The experiment does not authorize automatic migration of healthy work.
- The sync wire, signed route set, route binding, immutable-object identity, and Ratox framing remain
  unchanged.
- The small fixture establishes topology, not a throughput benefit. Counterbalancing removes the
  fixed-first policy-order bias, but does not randomize route startup or fault order; its post-gate
  Ratox interval is not scheduler-phase resource attribution.
- ADR 0172 subsequently closes the first bounded single-pull cancellation-tail row, and ADR 0173
  closes one bounded eight-job small-object population/resource row. Gate 4 remains open for
  randomized route startup/fault order, larger-object throughput/resource attribution, exact
  first-byte fairness, concurrent cancellation, and single-versus-independent TCP relay diversity.

## Verification

`tools/run-sandwurm-pair.py` constructs and checks the live overlap. The strict standalone verifier
rejects a primary carrier mistaken for an auxiliary assignment, unknown phase order, fixed carrier divergence, adaptive
carrier reuse, wrong decision or activation counts, unbounded retry totals, route-class disagreement,
or missing protected Ratox evidence. Its mutation self-test covers the additive receipt fields.
