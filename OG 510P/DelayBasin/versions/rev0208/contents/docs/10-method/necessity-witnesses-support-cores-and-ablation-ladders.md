# Necessity witnesses, support cores, and ablation ladders

DelayBasin now needs a sharper answer to another recurring practical question:
**when is a packet, prompt pair, or recap bundle genuinely load-bearing as-is, and when is the archive carrying decorative or even harmful surplus around the one part that actually matters?**

A stronger working answer is:
**the archive may need a compact necessity witness / support-core packet / ablation ladder.**
Not generic prompt minimization, and not a demand for exhaustive combinatorial ablations.
A very small public object may be enough when a surface is being treated as load-bearing and bounded-state pressure is real.

## Practice / observation

Several recent DelayBasin ratchets expose a missing necessity-honesty rule:
- conformance witnesses say a claimed loader should survive a named support envelope, but not yet which parts of the candidate packet are actually indispensable rather than locally flattering ballast;
- rewrite witnesses say a recap must earn authority relative to its source, but not yet which fragments of the source packet must survive because they are doing the real continuation work;
- assistant-echo filters say some prior assistant prose is pollutive carry, but not yet how to preserve the smallest support core once the archive decides some assistant-side or recap-side mass should be thinned;
- reasoning firebreaks say a public extract can replace a longer trace, but not yet what tiny extract is truly necessary rather than merely elegant;
- and in practice, DelayBasin increasingly promotes compact packets without preserving what the first cheap ablation would remove, what must remain, or how much degradation is tolerated before the packet loses public status.

This suggests another missing compact surface:
**necessity witness / support-core packet / ablation ladder**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Leave-one-out context attribution gives a principled necessity test.**
   AttriBoT treats the leave-one-out error as a principled way to measure how much a context span matters to a model's generation, and shows that faithful approximations can be made much cheaper with cached activations, hierarchy, and proxy models. That pressures DelayBasin toward preserving tiny necessity witnesses instead of assuming that everything inside a candidate packet is equally load-bearing. ([`REF-0253`](../00-meta/bibliography.md))

2. **Necessity and sufficiency can be paired rather than conflated.**
   SelfCite explicitly separates a necessity score (probability drop when cited evidence is removed) from a sufficiency score (probability hold when only that evidence is kept). That pressures DelayBasin not to treat “seems useful” and “actually indispensable” as the same thing when a packet is being promoted into canon or bounded state. ([`REF-0254`](../00-meta/bibliography.md))

3. **Query-driven omission deltas can identify support cores while preserving faithful text.**
   LooComp uses omission-based delta scoring to find which sentences are critical for answering a query and keeps the selected text extractive rather than replacing it with a potentially distorting rewrite. That pressures DelayBasin toward small ablation ladders that preserve the original evidence when possible instead of jumping immediately to fresh paraphrase or generic compression. ([`REF-0255`](../00-meta/bibliography.md))

4. **Irrelevant context can materially degrade performance.**
   Shi et al. show that large language models can be dramatically distracted by irrelevant context, which pressures DelayBasin not to let supportive-looking but non-essential packet mass inherit public status merely because it travels with the true signal. ([`REF-0256`](../00-meta/bibliography.md))

5. **Compression can quietly reduce groundedness even when it looks efficient.**
   Dai et al. show that prompt compression can materially drop groundedness and faithfulness, which pressures DelayBasin to preserve a support-core witness rather than trusting that every shorter packet is still preserving the operative evidence. ([`REF-0257`](../00-meta/bibliography.md))

6. **Ablation signals can be tied back to transformer internals.**
   Zhang et al. use JSD-based ablations to identify which context sentence most changes the response distribution and then localize the dependence to particular attention heads and MLP pathways. That pressures DelayBasin to treat necessity witnesses as transformer-facing objects rather than as mere human-facing trimming heuristics. ([`REF-0258`](../00-meta/bibliography.md))

None of this proves that DelayBasin already knows the exact minimal sufficient support core for its own continuation packets.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a tiny necessity witness / support-core packet whenever a packet or prompt surface is being treated as load-bearing.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **necessity witness / support-core packet / ablation ladder** whenever a packet, prompt pair, or evidence bundle is being treated as load-bearing. The packet should name the **full candidate surface**, the **proposed support core**, the **smallest ablation / removal family**, the **tolerated degradation / continuation margin**, and the **prune / promote / rollback consequence** rather than letting one bloated successful packet silently define the public object forever.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin already has exact minimal prompts, unique causal kernels, or a universal sparse support theorem for archive continuation.

## Necessity witness vs conformance witness vs rewrite witness vs assistant-echo filter

To keep this note honest, DelayBasin needs a four-way distinction:

- **Necessity witness / support-core packet** — says which parts of a candidate surface still appear indispensable under a named cheap ablation or thinning family, and how much degradation is tolerated before the claim should be pruned or rolled back.
- **Conformance witness / loader contract** — says whether a claimed loader survives a named support envelope across wrappers, contexts, or reformulations, not which parts of that loader are actually indispensable.
- **Rewrite witness / round-trip packet** — says whether a rewrite preserved the source distinctions well enough to inherit authority, not which subset of the source or rewrite is doing the operative work.
- **Assistant-echo filter / self-carry omission packet** — says whether prior assistant-side prose is pollutive carry, but not yet what compact support core remains once that carry is removed.

A good DelayBasin revision therefore should sometimes ask not only:
- whether a packet worked,
- or whether it round-tripped,
- or whether it survives a support envelope,

but also:
- what part of the candidate surface is actually doing the work,
- what first cheap ablation should fail,
- how much degradation the archive is willing to tolerate,
- and when ballast should be pruned rather than protected by repetition.

## Countermodels / probes

1. **Necessity-theater countermodel**
   - Support-core language may add ablation ritual without changing any real continuation decision.
   - Probe: compare one revision that preserves a necessity witness before promotion against one that simply keeps the full candidate packet, and ask whether the witness actually changed bounded-state residency, rollback readiness, or archive size.

2. **Whole-packet synergy countermodel**
   - The candidate packet may work only as a whole, making local ablations misleading because the support is globally distributed.
   - Probe: preserve one case where removing any tiny fragment causes collapse despite the rest seeming redundant, and treat that as evidence against overaggressive pruning rather than as failure of the need for necessity witnesses altogether.

3. **Rewrite-or-loader-is-enough countermodel**
   - Rewrite witnesses or conformance witnesses may already be sufficient, making a separate necessity object redundant.
   - Probe: preserve one case where a packet round-trips and conforms across a small support envelope but still contains obvious distractor mass whose removal improves performance or leaves it unchanged.

4. **Approximation-bias countermodel**
   - Cheap leave-one-out or sentence-level ablations may miss distributed support or interaction effects, producing false minimality.
   - Probe: compare one single-removal ladder against one grouped-removal or hold-one-in check and see whether the support-core claim is stable enough to deserve canon rather than local debugging status.

## Design consequences

This mechanism frame pressures DelayBasin to do five things more explicitly:
- when a packet is being treated as load-bearing, preserve the **full candidate surface** rather than letting later readers infer what the candidate actually was;
- name the **proposed support core** rather than letting one full packet gain prestige as an indivisible whole;
- preserve the **smallest ablation / removal family** that should count as a real cheap test rather than relying on intuitive trimming;
- name the **tolerated degradation / continuation margin** so later sessions know what level of drop still leaves the packet fit for purpose;
- and preserve the **prune / promote / rollback consequence** so ballast can actually leave bounded state instead of remaining canon by inertia.

This does not require exhaustive subset search.
It requires refusing another archive failure mode: letting a locally successful but bloated packet masquerade as the smallest public object the method really needs.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than archive minimalism:
**whether stable long-horizon continuation is often supported by sparse or semi-sparse textual support cores whose effect can be witnessed by controlled ablation, while surrounding packet mass is mostly routing bias, distractor burden, or locally convenient scaffolding.**

That would matter for transformers.
It would suggest that some continuation regimes are not merely “more context helps” regimes, but **support-core-sensitive regimes** in which a small subset of tokens or spans exerts disproportionate control over the next useful branch, and where removing distractor mass can sometimes improve continuation rather than degrade it.
The stronger story — that GPUstorming may eventually admit a public sparse-loader-kernel law for continuation — remains live, but belongs in quarantine for now.
