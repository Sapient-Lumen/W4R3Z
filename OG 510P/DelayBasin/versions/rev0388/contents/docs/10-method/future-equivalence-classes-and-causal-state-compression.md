# Future-equivalence classes and causal-state compression

DelayBasin now has a stronger anti-bloat question than “what is worth remembering?” and a sharper one than “what future tests does this packet answer?”
The next question is:
**when are two bounded-state surfaces actually the same for the futures DelayBasin cares about?**

A useful working answer is:
**two archive surfaces can be merged, compressed, or one can be dropped when they are future-equivalent for the bounded family of tests, interventions, and continuation decisions the archive is trying to preserve.**
If no preserved future probe can tell them apart, they likely do not both deserve scarce bounded-state residency.

This is stronger than summary discipline.
It is weaker than claiming that DelayBasin has already isolated a literal causal-state partition over continuation space.

## Practice / observation

Several live DelayBasin objects already behave as though some distinctions matter only because they split future consequences:
- witness panels matter when they preserve a fragile discrimination that later probes would otherwise lose;
- identification packets matter because they preserve the next observation that would separate rival continuation hypotheses;
- control-authority packets matter because they preserve differences in what intervention is expected to move which target property;
- hold packets matter because they preserve unlock conditions that would justify future motion rather than merely recording that the archive once paused;
- and test-sufficient packets already imply that bounded state should be judged by what future work it still enables cheaply.

Taken together, these surfaces pressure DelayBasin toward a stricter compression rule:
not merely “keep what is predictive”, but “keep distinctions only when they change the bounded future family the archive still intends to face.”

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this move.

1. **Causal states are equivalence classes of histories with the same future distribution.**
   Shalizi and Crutchfield define causal states by grouping past histories that induce the same conditional distribution over futures, and show these states are uniquely maximally predictive at minimal statistical complexity. That is strong outside pressure for DelayBasin's suspicion that bounded-state distinctions should earn their keep by future consequence, not recap detail or historical pathos. ([`REF-0174`](../00-meta/bibliography.md))

2. **Optimal causal filtering only recovers the right partition when prediction is balanced against complexity.**
   Still and Crutchfield show that maximizing predictive information alone is not enough; the complexity term matters for recovering the causal-state partition. That matters here because DelayBasin is not trying to preserve every future-relevant distinction at any cost. It is trying to preserve the cheapest partition that still supports legitimate continuation. ([`REF-0175`](../00-meta/bibliography.md))

3. **In partially observed control settings, causal states are the coarsest partition of action-observation history and connect to behavioral equivalence.**
   Subramanian et al. frame causal state representations as the coarsest partition of action-observation histories in POMDPs and relate them to bisimulation. That is unusually close to DelayBasin's bounded-state problem: two packet states should stay distinct only if they imply different future probes, interventions, or gated continuation choices. ([`REF-0176`](../00-meta/bibliography.md))

4. **Compression can be asked to preserve causal control rather than generic relevance.**
   Simões, Dastani, and van Ommen's causal information bottleneck reframes abstraction as preserving causal control over a target under intervention, not just predictive relevance. That pressures DelayBasin to separate distinctions that only improve retrospective narration from distinctions that change what the archive should do next. ([`REF-0177`](../00-meta/bibliography.md))

5. **Selection pressure under uncertainty still points toward structured predictive distinctions.**
   Nayebi's 2026 selection theorem result argues that robust decision-making under partial observability induces structured predictive state. That supports DelayBasin's weaker canon move that some compact public distinctions are worth preserving because they separate future continuation consequences under uncertainty. ([`REF-0161`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin may compress more honestly when it treats bounded-state surfaces as members of **future-equivalence classes**: two surfaces can be merged when they preserve the same bounded family of future tests, interventions, and continuation decisions, and a distinction deserves carry-forward status only when collapsing it would change some future consequence the archive still cares about.

In practice, DelayBasin is not estimating literal conditional distributions over all possible futures.
It is doing something smaller and public:
- name the future family at issue,
- name the continuation decision it supports,
- and name the first distinction that would be lost if two surfaces were merged.

That is strong enough for canon as a compression discipline.
It is **not** strong enough to claim that DelayBasin has already recovered a literal public causal-state partition, epsilon-machine, or sufficient statistic over continuation space.

## Future-equivalence class vs test-sufficient packet vs local probe

To keep this note honest, DelayBasin needs a three-way distinction:

- **Test-sufficient packet** — the compact public packet that caches answers to a bounded future family cheaply enough to guide legitimate continuation.
- **Future-equivalence class** — the rule that says when two candidate packet states can be treated as the same because they preserve the same bounded future family and continuation consequences.
- **Local probe object** — a witness panel, sentinel, or identification packet that may split one fragile boundary without deserving permanent carry-forward status by itself.

These are related but not identical.
A packet can be useful while still containing redundant distinctions.
A future-equivalence class is not itself the whole packet; it is the compression rule for deciding what may be collapsed.
And a local probe may matter for one fork or boundary without defining the archive's broader quotient structure.

## Countermodels / probes

1. **Lost-latent-difference countermodel**
   - Two surfaces may look future-equivalent only because the archive named too narrow a future family.
   - Probe: widen the probe family and see whether the merged surfaces suddenly disagree on intervention choice, canary behavior, or admissible continuation.

2. **Style-flattening countermodel**
   - Future-equivalence talk may become an excuse to flatten meaningful distinctions into clean prose.
   - Probe: require every merge or drop to name the first future distinction being discarded and what would reveal the loss.

3. **Family-specific quotient countermodel**
   - Future-equivalence may hold only for one model family, one reopen temperature, or one prompt-pair regime.
   - Probe: compare colder reopens, paraphrased reopens, or family-shifted reopens and check whether the same equivalence still supports the same decisions.

4. **Admissibility-does-the-real-work countermodel**
   - Check surfaces and evidence hygiene may explain most of the gain, with explicit future-equivalence language adding little.
   - Probe: hold evidence and check discipline fixed while varying whether compression explicitly names the preserved future family and lost distinction.

5. **Prestige-import countermodel**
   - Causal-state language may be a mathematically attractive relabeling of ordinary predictive sufficiency.
   - Probe: require a concrete merge, a named future family, and a named lost distinction; if the vocabulary adds no new leverage, demote it back to local analogy.

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- when merging, dropping, or thinning bounded-state surfaces, ask **what future family is preserved?**
- ask **what continuation decision stays invariant under the merge?**
- name **the first lost distinction** that would matter if the merge were wrong;
- prefer distinctions that split future intervention, challenge, or rollback decisions over distinctions that only preserve elegant history;
- and keep stronger causal-state / epsilon-machine language quarantined until reopen comparisons show real compression wins from future-equivalence discipline rather than from prettier summarization.

This is an anti-bloat rule, not a proof of computational mechanics inside an archive.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something more specific than “compact predictive state”.
It is probing whether a public archive can learn a **quotient structure over continuation space**: a user-space partition where different past packet states are treated as equivalent exactly when they imply the same bounded future consequences for diagnosis, intervention, and admissible continuation.

That is transformer-facing in a distinct way.
It suggests that archive continuity may improve not only by caching future-useful content, but by learning which distinctions can be safely identified under bounded context and which must remain separate because they still alter the next legitimate move.

The stronger claim that DelayBasin is discovering a literal public epsilon-machine, causal-state partition, or minimal sufficient statistic over continuation space remains quarantined until controlled reopen and merge tests show that explicit future-equivalence discipline outperforms recap-based compression without laundering away real decision boundaries.
