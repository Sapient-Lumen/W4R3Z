# Research notes — rev0153

## Question

How should an immutable plural-world ledger repair current planning weights after one of their supporting evidence assertions is withdrawn, without erasing what the planner previously believed or pretending that arithmetic history is canon?

Rev0152 deliberately stopped at visible reweighting debt. Rev0153 turns that debt into an explicit reason-maintenance protocol.

## 1. The useful distinction: historical action versus current support

An old particle update can remain a valid historical statement even after its evidence is no longer accepted:

> At sequence 42, the planner used assertion A as one complete likelihood factor and changed the bank from P to Q.

What becomes invalid is a different statement:

> Q is still the distribution implied by the currently authorized factor set.

Deleting or rewriting the update confuses those statements. Leaving Q untouched and calling it current also confuses them. The safe representation is a second event that preserves the first and repairs the derived surface.

This closely resembles truth or reason maintenance: record why a derived state was supported, then revise that state when assumptions change while retaining dependency history. Doyle's 1979 truth-maintenance system was designed around the need to make assumptions and subsequently revise consequences. Lacuna does not import its in/out belief semantics wholesale, but it adopts the central custody lesson: **support must be inspectable if retraction is expected**.

Source: Jon Doyle, [A Truth Maintenance System](https://dspace.mit.edu/handle/1721.1/5733), MIT AI Memo 521, 1979.

## 2. Why a new event is better than mutable posterior repair

Event sourcing separates immutable facts about transitions from rebuildable current projections. Fowler's formulation explicitly notes both state reconstruction and retroactive correction as uses of an event log. For Lacuna, that means:

- `particle.updated` remains immutable evidence of a past planning transition;
- `particle.reconciled` records a later factor-selection decision and replay result;
- current world weights are rebuilt by applying both in sequence.

A destructive SQL correction would make verification unable to answer when, why, and under which ledger head the factor stopped contributing. An inverse multiplication would be numerically fragile, fails for zero likelihood, and assumes that floating-point operations can be exactly undone. Full replay from an immutable baseline is simpler to explain and audit.

Sources:

- Martin Fowler, [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html), 2005.
- Martin Fowler, [Retroactive Event](https://martinfowler.com/eaaDev/RetroactiveEvent.html), 2005.

## 3. Why the baseline comes from the first factor receipt

Possible baselines considered:

1. **Current raw weights divided by removed likelihoods.** Rejected: division cannot recover zeroed mass, compounds rounding error, and is undefined for zero likelihood.
2. **The campaign's initial world weights.** Rejected: structural changes and intentional manual prior changes make a global beginning unrelated to the present population.
3. **A newly authored replacement prior.** Useful in another protocol, but it would combine repair with a fresh modeling decision.
4. **The prior snapshot of the first update in the latest coherent epoch.** Chosen: it is immutable, complete, already event-bound, and exactly the distribution against which the epoch's factor chain began.

The fourth option lets reconciliation remain derived repair rather than prior authoring.

## 4. Why structural epochs are conservative

A factor's likelihood vector was assessed against a specific population and recorded status/valuation/custody fingerprint for each world. Reusing it after a world mutation would silently assume semantic invariance.

Rev0153 starts a new epoch after:

- world creation;
- assignment or governed revision;
- commitment raise;
- manual weight change; or
- status change.

This is stricter than mathematically necessary in some cases. A commitment raise, for example, might not change the truth conditions relevant to a likelihood. But Lacuna cannot prove that irrelevance, and the custody fingerprint deliberately treats commitment as material planning state. The conservative boundary avoids laundering stale judgments.

Future work could support an explicit **factor portability review** that reauthorizes an old likelihood vector against a new custody surface. Automatic portability would be unsafe.

## 5. Why log-space replay matters even though updates normalize every step

Sequential normalized multiplication reduces many underflow risks, but it does not eliminate them. A world with tiny current probability multiplied by a tiny positive likelihood can underflow to zero while another world remains representable. Later normalized updates cannot recover it because zero is absorbing under multiplication.

Replay computes:

```text
log score = log baseline probability + sum(log likelihood)
```

and normalizes after subtracting the maximum log score. This preserves relative positive mass across long chains as far as ordinary floating-point exponentiation permits. SciPy exposes the same numerical pattern in `logsumexp`; Lacuna implements the scalar standard-library equivalent to keep runtime dependencies at zero.

Source: [SciPy `scipy.special.logsumexp`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.logsumexp.html).

A regression test simulates 140 tiny factors where sequential multiplication has already lost one world's mass. Reconciliation recovers the mathematically positive posterior near `1e-140`.

## 6. Particle filtering is a metaphor with limits

Sequential Monte Carlo supplies useful language:

- particles as alternative latent hypotheses;
- weights as relative planning attention;
- effective sample size and entropy as concentration diagnostics;
- degeneracy and impoverishment as warnings.

Doucet and Johansen stress that ESS is a surrogate and can be misleading when the underlying particle approximation is poor. Lacuna therefore does not interpret a high ESS as diversity, a low ESS as proof of a winner, or normalized weights as calibrated belief.

Source: Arnaud Doucet and Adam Johansen, [A Tutorial on Particle Filtering and Smoothing](https://www.stats.ox.ac.uk/~doucet/doucet_johansen_tutorialPF2011.pdf).

Rev0153 still performs no resampling. Reconciliation changes weights over the same complete eligible population. Birth, ancestry, merging, minority preservation, and pruning remain distinct future protocols.

## 7. Why factor selection follows assertion activity

The epistemic ledger already knows whether an assertion is active or ended. Reconciliation uses that recorded state rather than asking a model to reinterpret prose:

- active assertion → included factor;
- ended assertion → excluded factor.

This is intentionally mechanical. It does not judge whether the superseding assertion truly invalidates the original evidence, whether two reports share one cause, or whether an ended assertion should be replaced by another factor. Those are authored epistemic acts and need their own custody.

The result is a minimal truth-maintenance rule with strong auditability.

## 8. Why excluded factors remain first-class records

An excluded factor is not garbage. It can explain:

- why an earlier scene was planned differently;
- why a world temporarily received high attention;
- when the planner learned that support was withdrawn;
- whether a later reconciliation actually responded;
- whether a host selectively hid an inconvenient update.

The reconciliation factor projection therefore records both included and excluded rows. `particle-bank` labels historical factors by epoch and resolution instead of presenting only the active set.

## 9. Why a reconciliation can be a no-op

The current bank may already equal replayed active factors. A first reconciliation can still be meaningful because it:

- verifies the ledger under log-space arithmetic;
- establishes an immutable factor-set receipt;
- proves that no hidden repair was required; and
- creates a stable audit target.

Repeated reconciliation of the same factor set and identical posterior is refused. This balances audit value against event spam.

## 10. Authority and confidentiality

The complete denominator is privileged hidden-world state. A reconciliation review exposes:

- every eligible world;
- every factor ID;
- which evidence ended;
- per-world likelihood effects; and
- the current and repaired distributions.

It is therefore available only to unscoped planner context, direct host/Python access, and the host CLI. World-scoped director context cannot safely authorize a global replay from a filtered view. Audience context omits the entire surface, including counts and IDs.

This extends Lacuna's context-firewall doctrine rather than adding a redaction pass after privileged construction.

## 11. Alternatives rejected

### Mutate the original update

Rejected because it falsifies historical custody and makes event replay nondeterministic across software versions.

### Append an inverse factor

Rejected because zero likelihood has no inverse, correlated floating-point error accumulates, and the inverse factor would not clearly express evidence withdrawal.

### Automatically reconcile whenever an assertion ends

Rejected because assertion supersession and global weight repair are separate authority domains. Automatic coupling would make a local epistemic edit mutate hidden-world planning state as an undeclared side effect.

### Replay every factor since campaign creation

Rejected because likelihoods are not portable across changed populations and world custody.

### Select the highest-weight world after repair

Rejected because arithmetic repair is not canonization. A maximum remains a planner quantity, not truth.

### Let an LLM choose which factors still count

Rejected for the kernel. A model may propose assertion supersession or future factor-family metadata, but deterministic custody should not depend on an unrecorded semantic judgment.

## 12. Audit/refactor findings

The rev0153 implementation audit found two duplications in the particle path:

- live-bank construction and historical-bank reconstruction had parallel normalization logic;
- valuation-equivalent likelihood divergence was recomputed separately in update presentation and verification.

Both now live in `src/lacuna/particles.py` as shared pure functions. The reconciliation computation is also pure and receives explicit banks and factor receipts. SQLite orchestration remains in `store.py`.

A second audit found that schema-7 cubes with legitimate particle rows could be mistaken for the schema-6 dormant-table collision during migration preflight. The unowned-row refusal is now gated strictly to source schema 6; schema 7 migrates to schema 8 while preserving particle custody.

## 13. What this still does not solve

### Evidence dependence

Single-use assertion IDs stop exact duplicate multiplication, but two assertions can describe the same underlying observation. A future factor-family or dependence graph should make shared causal provenance inspectable. Naively multiplying correlated factors remains a major risk.

### Factor correction rather than withdrawal

Rev0153 can include or exclude an immutable factor. It cannot replace a mistaken likelihood vector while preserving an explicit predecessor/successor relation. A future protocol should resemble consequence replacement: review the old factor, author a complete successor vector, and record one-to-one lineage.

### Portable factors across epochs

A structurally changed world bank requires new assessments. A future portability receipt might prove that a factor was re-reviewed against every new fingerprint, but no automatic carry-over should be inferred.

### Arbitrary precision and deterministic cross-runtime floats

Log-space avoids ordinary underflow but still uses IEEE-754 doubles. Exact reproducibility is tested within the supported Python/SQLite environment; Lacuna does not yet define a decimal or rational wire arithmetic standard.

### Resampling and population health

Reconciliation does not create missing hypotheses or preserve low-mass alternatives. Future proposal/resampling work needs ancestry, minority reserves, semantic clustering, and inspectable diversity policy.

### Causal agency

A repaired distribution can make player actions look consequential without proving that outcomes would differ under a nearby counterfactual. Lacuna still needs explicit counterfactual probes if it is to distinguish interpretive incorporation from causal agency.

## 14. Bold next hypotheses

1. **The factor ledger will become a typed dependency graph, not a list.** Assertions will name observation families, conditional parents, and mutual-exclusion relations so the engine can refuse naïve correlated multiplication.
2. **Reconciliation checkpoints will become portable audit artifacts.** A host may externally sign a factor-set digest and later prove exactly which hidden-world distribution was in force without revealing every world at publication time.
3. **World proposal will be triggered by explanatory residuals, not merely low ESS.** When every surviving world assigns low likelihood to an observation, the right action is probably to propose a missing hypothesis rather than concentrate harder on bad ones.
4. **Narrative fairness will use dual custody:** adaptive factors for flexible drama, cryptographic seals for selected non-adaptive secrets. The tension between them is a feature, not a defect.
5. **A mature Lacuna host will run counterfactual twin turns.** It will replay nearby player choices against the same sealed/factor state and report whether differences are causal, merely interpretive, or absent.

## 15. Conclusion

Gwern's delayed-commitment intuition becomes safer when hidden worlds are plural and their support is reason-maintained. Rev0153's central move is small but foundational:

> Do not retcon the old posterior. Preserve the old decision, recompute the current support from an immutable baseline, and record the repair as a new fact.

That gives Lacuna a mechanism for changing its mind without changing its memory.
