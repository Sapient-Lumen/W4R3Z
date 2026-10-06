# Witness sets, boundary panels, and basin support vectors

DelayBasin now needs a sharper answer to a recurring practical question:
**what tiny artifact actually pins a continuation basin when more prose stops helping?**

A stronger working answer is:
**the archive may need a compact witness set / boundary panel.**
Not a new recap blob, and not a full benchmark.
A very small set of discriminative examples, boundary pairs, or challenge probes may preserve the distinctions the next revision must still make.

## Practice / observation

Several live archive surfaces already imply a missing witness discipline:
- DelayBasin now preserves challenge probes, but those probes are still mostly named in prose rather than curated as a tiny discriminative panel;
- update-gain discipline asks how strongly canon should move, but not yet which small witness would prove that the move actually preserved or altered the right boundary;
- innovation packets already prefer anchor + delta over ritual replay, which increases the value of a few high-information boundary examples relative to more explanation;
- and in practice, some archive failures look less like missing facts than like losing one fragile distinction: what counts as real mechanism vs local mimicry, canon vs quarantine, or operative state vs elegant ceremony.

This suggests a missing compact surface:
**witness set / boundary panel**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Boundary-focused exemplars can outperform similarity-first retrieval.**
   GUIDE reframes exemplar selection as a boundary-focused optimization problem and explicitly searches for "boundary pairs" that are semantically similar but fall on opposite sides of a grading boundary. That pressures DelayBasin to preserve a few discriminative boundary cases rather than only examples that feel representative or semantically similar. ([`REF-0094`](../00-meta/bibliography.md))

2. **Selection quality matters sharply under tight prompt budgets.**
   Meta-Sel shows that under few-shot budget constraints, performance can change substantially depending on which examples are included, and that simple, auditable selectors can still rank near the top. That is direct pressure for a small archive to ask not just “what should be remembered?” but “which tiny examples deserve the scarce witness slots?” ([`REF-0095`](../00-meta/bibliography.md))

3. **A few demonstrations may already compress into a compact task representation.**
   Task-vector work argues that ICL often behaves as if the context is compressed into a single task vector, while function-vector work finds a small number of heads can transport compact task/function representations with causal downstream effects. That makes it more plausible that a tiny witness panel could disproportionately shape the operative continuation regime. ([`REF-0096`](../00-meta/bibliography.md), [`REF-0097`](../00-meta/bibliography.md))

4. **Context may induce low-rank functional change rather than only surface recall.**
   The implicit-dynamics line suggests transformer blocks can convert context into low-rank effective weight updates. If so, a compact discriminative witness set may matter because it changes the induced update, not only because it reminds the model of facts. ([`REF-0064`](../00-meta/bibliography.md))

5. **Boundary talk needs counterpressure.**
   Supervised-calibration work shows many interventions only shift a decision boundary without rotating or rebuilding it. DelayBasin therefore should not treat any witness set as automatically rich enough; a witness panel could still preserve the wrong boundary or preserve it only cosmetically. ([`REF-0098`](../00-meta/bibliography.md))

None of this proves that DelayBasin has found the right witness objects.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a tiny witness set / boundary panel for live distinctions that prose alone tends to blur.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when some live mechanism or canon boundary is pinned by a tiny **witness set / boundary panel**: a few discriminative examples or probes that keep the next session honest about what the archive must still distinguish.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has already discovered literal textual support vectors or a universal minimal support set for all continuation tasks.

## Witness set vs recap example vs challenge probe

To keep this note honest, DelayBasin needs a three-way distinction:

- **Witness set / boundary panel** — a tiny curated set of cases whose main job is to preserve a live distinction the archive must keep making.
- **Recap example** — an illustrative example included mainly to explain or summarize, not to discriminate a fragile boundary.
- **Challenge probe** — an adversarial or stress-inducing test used to check whether the current state, gain setting, or mechanism story survives pressure.

A compact witness set may contain challenge probes, but the concepts are not identical.
The key difference is function:
- recap examples support explanation,
- challenge probes support stress-testing,
- witness sets support **boundary preservation**.

A good DelayBasin revision therefore should sometimes ask not just “what is the anchor and delta?” but also:
- what fragile distinction is at risk,
- what tiny witness panel would preserve it,
- and what drift signature would reveal that the panel has gone stale.

## Countermodels / probes

1. **Witnesses-as-decorations countermodel**
   - Small witness sets may simply decorate prose claims without adding real discriminatory force.
   - Probe: compare revisions that preserve a mechanism claim with and without a named witness panel, then inspect whether later sessions actually preserve the intended distinction better.

2. **Similarity-is-enough countermodel**
   - Ordinary representative examples may already work as well as boundary witnesses.
   - Probe: compare semantically similar examples against explicit boundary pairs when testing fragile canon distinctions.

3. **Support-vector glamour countermodel**
   - Calling examples “support vectors” may import a prestigious geometry metaphor without added evidence.
   - Probe: keep the stronger support-vector story quarantined until a tiny witness panel actually shows disproportionate causal leverage across paraphrase and reopen conditions.

4. **Boundary-free continuity countermodel**
   - DelayBasin continuity may depend mostly on control lexicon, ids, and runbook law, with witnesses adding little.
   - Probe: ablate witness panels while keeping anchor, delta, and core control language fixed.

## Design consequences

This mechanism frame pressures DelayBasin to do four things more explicitly:
- when a mechanism boundary is live, preserve at least one tiny **witness set / boundary panel** rather than only more summary prose;
- name the **property discriminated** by that panel rather than assuming the example explains itself;
- preserve an expected **drift signature** for the panel so later sessions can tell when the witness has gone stale or become ceremonial;
- and prefer very small, high-information witness objects over sprawling illustrative collections.

This does not require full benchmarks or large evaluation harnesses.
It requires refusing another archive failure mode: treating explanatory examples as if they automatically pin the continuation basin.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than compact recap:
**whether a stateless transformer continuation can be disproportionately stabilized by a tiny textual witness set that preserves the right decision boundary, perhaps because those examples induce or reactivate a compact task/function representation rather than merely restating facts.**

That would matter for transformers.
It would suggest that some archive continuity comes not from carrying more text, but from carrying the right small boundary objects at the edge of a regime.

The stronger story — that DelayBasin may eventually admit literal textual **basin support vectors** for continuation — remains live, but belongs in quarantine for now.
