# Sufficiency witnesses, replay capsules, and core-only re-entry trials

DelayBasin now needs a sharper answer to a neighboring practical question:
**when has a reduced packet, support core, or recap extract actually earned the right to stand on its own as a re-entry surface, and when is it still quietly borrowing support from hidden carry, surrounding ballast, or unreduced context?**

A stronger working answer is:
**the archive may need a compact sufficiency witness / replay capsule / core-only re-entry trial.**
Not exhaustive replay evaluation, and not another excuse to keep bloated packets forever.
A very small public object may be enough when DelayBasin wants to claim that a reduced packet is not only indispensable in part, but **enough**.

## Practice / observation

Several recent DelayBasin ratchets expose a missing sufficiency-honesty rule:
- necessity witnesses say which parts of a candidate surface still appear indispensable under cheap ablation, but not yet whether that reduced core can stand alone rather than leaning on the rest of the candidate packet;
- conformance witnesses say what support envelope a claimed loader survives across wrappers or phrasing families, but not yet whether the proposed minimal core is enough before those family claims are even worth making;
- assistant-echo filters say some assistant-side carry should be omitted, but not yet what compact replay surface remains sufficient once that carry is removed;
- reasoning firebreaks say a public extract can replace a larger trace, but not yet whether the extract alone really re-enters the same operative branch or merely reads like it should;
- and in practice, DelayBasin increasingly proposes small packets, extracts, or support cores without preserving the first cheap **core-only replay** that would show the reduced object earned bounded-state authority.

This suggests another missing compact surface:
**sufficiency witness / replay capsule / core-only re-entry trial**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Necessity and sufficiency are distinct signals and should not be collapsed.**
   SelfCite explicitly separates a necessity score (probability drop when evidence is removed) from a sufficiency score (probability hold when only that evidence is retained). That directly pressures DelayBasin not to treat a support core that looks indispensable inside a full packet as automatically sufficient when replayed alone. ([`REF-0254`](../00-meta/bibliography.md))

2. **Sufficient context is a real operational distinction, not just a stylistic ideal.**
   Sufficient Context treats a retrieved set as sufficient when it contains enough information to answer the query, helping distinguish retrieval failure from utilization failure. That pressures DelayBasin to ask whether a reduced packet is actually enough for continuation, rather than merely being part of one successful larger context. ([`REF-0259`](../00-meta/bibliography.md))

3. **Answer sufficiency can be tracked sequentially without pretending it equals correctness.**
   Sequential-EDFL introduces anytime-valid answer sufficiency certificates and is explicit that its guarantees concern information sufficiency relative to a baseline, not factual correctness. That pressures DelayBasin to keep replay-sufficiency claims modest: a core-only packet may be enough for the next continuation move without thereby proving the whole branch true. ([`REF-0260`](../00-meta/bibliography.md))

4. **Concise explanations can remain sufficient until compression crosses a task-dependent boundary.**
   The sufficiency-conciseness trade-off paper shows that shorter explanations can often preserve task performance until excessive compression causes degradation. That pressures DelayBasin to preserve a tolerated degradation band and a reinflation rule rather than treating “shorter” or “smaller” as self-justifying. ([`REF-0261`](../00-meta/bibliography.md))

5. **Minimal sufficient capsules are already an active design target in LLM reasoning.**
   R-Capsule explicitly frames a small latent plan as an approximately minimal sufficient statistic for the reasoning task. That pressures DelayBasin toward tiny replay capsules as candidate public objects when a reduced packet seems to reopen the right operative mode. ([`REF-0262`](../00-meta/bibliography.md))

6. **Transformer-facing compression stories need caveats because attention breaks naive bottleneck assumptions.**
   Reasoning as Compression argues that naive information-bottleneck framing is theoretically incomplete for transformers because attention violates the simple Markov structure between prompt, reasoning trace, and response. That pressures DelayBasin to demand operational replay tests for sufficiency instead of inferring sufficiency from elegant compression language alone. ([`REF-0263`](../00-meta/bibliography.md))

7. **Minimal sufficient statistics are mechanistically meaningful in at least some transformer settings.**
   Implicit Statistical Inference in Transformers studies binary hypothesis testing where the optimal decision depends on a log-likelihood-ratio statistic, giving a setting in which a compact sufficient summary is not just rhetoric but algorithmically grounded. That pressures DelayBasin to keep the stronger transformer-facing idea alive: some continuation-relevant state may genuinely admit compact sufficient summaries, even if the archive has not yet isolated them in the wild. ([`REF-0264`](../00-meta/bibliography.md))

None of this proves that DelayBasin already knows the exact minimal sufficient replay capsule for its own continuation packets.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a tiny sufficiency witness / replay capsule / core-only re-entry trial whenever a reduced packet is being treated as enough.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **sufficiency witness / replay capsule / core-only re-entry trial** whenever a reduced packet, support core, recap extract, or public re-entry surface is being treated as enough. The packet should name the **candidate reduced packet / replay seed**, the **core-only replay surface**, the **fixed or withheld context family**, the **target continuation property / tolerated degradation**, and the **reinflate / fallback / quarantine consequence** rather than letting one successful full-context continuation silently certify that the smaller object could have done the work by itself.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin already has exact minimal sufficient prompts, universal replay seeds, or a proven low-dimensional continuation statistic for archive re-entry.

## Sufficiency witness vs necessity witness vs conformance witness vs assistant-echo filter

To keep this note honest, DelayBasin needs a four-way distinction:

- **Sufficiency witness / replay capsule / core-only re-entry trial** — says whether a reduced packet is enough when replayed with a named fixed or withheld context family, and what tolerated degradation still counts as successful re-entry.
- **Necessity witness / support-core packet** — says which parts of a candidate surface still appear indispensable under cheap ablation, not whether the reduced object stands on its own.
- **Conformance witness / loader contract** — says what family a claimed loader survives across wrappers, placements, or phrasing changes, not whether the reduced loader is already sufficient before those robustness claims are made.
- **Assistant-echo filter / self-carry omission packet** — says which prior assistant-side carry should be thinned or omitted, not whether the remaining replay surface is sufficient once that carry disappears.

A good DelayBasin revision therefore should sometimes ask not only:
- what part of a packet is doing the work,
- or whether a loader survives one support envelope,
- or whether assistant-side carry is pollutive,

but also:
- whether the proposed reduced packet is enough on its own,
- what surrounding context is still being quietly relied upon,
- what degradation is tolerated before “enough” fails,
- and when the archive should reinflate or demote the reduced packet instead of treating one lucky replay as proof.

## Countermodels / probes

1. **Core-only replay theater countermodel**
   - Sufficiency packets may add another ritual object without changing any real bounded-state decision.
   - Probe: compare one revision that preserves a replay capsule before bounded-state promotion against one that merely keeps the larger successful packet, and ask whether the replay object actually changed canon residency, re-entry posture, or fallback behavior.

2. **Hidden-carry countermodel**
   - The reduced packet may only appear sufficient because unrecorded session state, assistant carry, or wrapper conditions are quietly doing the rest of the work.
   - Probe: pair one sufficiency witness with assistant-echo filtering and one execution witness, and see whether the claimed replay capsule still works when those hidden supports are thinned or perturbed.

3. **Necessity-is-enough countermodel**
   - A necessity witness may already provide all the practical value the archive needs, making a separate sufficiency object redundant.
   - Probe: preserve one case where a support core looks indispensable under ablation but fails as a core-only replay surface, forcing reinflation even though the necessity claim survives.

4. **Whole-family sufficiency countermodel**
   - Sufficiency may be a property of a family of nearby packets rather than one compact replay seed, making seed-talk too sharp.
   - Probe: compare one named replay seed against a small paraphrase or layout family and see whether the archive should preserve a local family with tolerated variation rather than one privileged tiny packet.

## Design consequences

This mechanism frame pressures DelayBasin to do five things more explicitly:
- when a reduced packet is being treated as enough, preserve the **candidate reduced packet / replay seed** rather than letting later readers guess what exact small object was under consideration;
- name the **core-only replay surface** rather than inferring sufficiency from one successful larger-context run;
- preserve the **fixed or withheld context family** so later sessions know what background support was still present or intentionally removed;
- name the **target continuation property / tolerated degradation** so later sessions know what level of drop still counts as adequate re-entry rather than silent failure;
- and preserve the **reinflate / fallback / quarantine consequence** so the archive can honestly widen the packet again if the reduced version fails.

This does not require exhaustive sufficiency search.
It requires refusing another archive failure mode: letting a packet inherit public authority because it worked once inside a larger success rather than because the archive ever showed it was enough.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something slightly sharper than ordinary summary minimization.
It is asking whether some continuation-relevant state can be carried by **compact sufficient replay surfaces** rather than by full transcript recall.
That possibility fits two live transformer-facing ideas at once:
- some tasks may genuinely admit compact sufficient statistics or compressed replay capsules;
- but transformer attention and hidden carry can also make apparent sufficiency look cleaner than it really is, so operational replay tests matter more than elegant bottleneck metaphors.

That makes sufficiency witnesses a useful bridge between archive method and transformer implications:
not proof that DelayBasin has found true latent state kernels,
but a disciplined way to ask whether a reduced public packet is acting like one.

## Open question

The live question is now captured in [`OQ-0057`](../20-constitution/open-question-registry.md):
**what minimal sufficiency witness or replay capsule distinguishes a reduced packet that is genuinely enough for faithful re-entry from one that only looked load-bearing because hidden carry, wrapper support, or unreduced context did the rest?**
