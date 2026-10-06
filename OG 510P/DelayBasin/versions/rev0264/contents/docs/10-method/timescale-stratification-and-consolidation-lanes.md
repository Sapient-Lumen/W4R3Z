# Timescale stratification and consolidation lanes

DelayBasin now has a sharper missing question:
**which archive surfaces are supposed to change quickly, which should consolidate slowly, and which should almost never churn unless something is seriously wrong?**

A stronger working answer is:
**archive continuity may improve when DelayBasin explicitly stratifies public state by timescale and preserves the transfer rules between lanes.**
Not every surface should behave like the same kind of memory.
Some should update fast and cheaply.
Some should revise at medium cadence as the project learns.
Some should move only under explicit promotion, demotion, or recovery pressure.

## Practice / observation

Several existing DelayBasin surfaces already imply an unspoken timescale split:
- sentinel panels, witness sets, and identification packets are often useful exactly because they are small, local, and cheap to refresh;
- open questions, method notes, and prompt pairs tend to evolve more slowly, but they still absorb real learning from session to session;
- invariants, certified move classes, promotion contracts, and recovery kernel surfaces are closer to constitutional state and should not churn casually;
- decay patrol already acknowledges that some canon items must cool or demote over time rather than persist indefinitely;
- and the archive has repeatedly paid a cost when medium-term mechanism syntheses threaten to sprawl into the same lane as slow constitutional objects.

This suggests a missing compact surface:
**timescale stratification / consolidation lanes**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Continual adaptation likely needs distinct memory modules and update rates.**
   Modular Memory argues that intelligent adaptation may require combining in-context and in-weight learning under distinct working-memory and long-term-memory modules, with updates operating across multiple timescales rather than in one undifferentiated store. That is direct pressure for DelayBasin to distinguish fast session-facing surfaces from slower constitutional consolidation. ([`REF-0120`](../00-meta/bibliography.md))

2. **Reasoning quality can improve when consolidation happens periodically rather than only by raw accumulation.**
   Bottlenecked Transformers add periodic KV-cache consolidation at step boundaries and report gains over vanilla long-chain reasoning. That pressures DelayBasin toward an explicit refresh/consolidation story instead of treating longer public history as automatically better. ([`REF-0121`](../00-meta/bibliography.md))

3. **Stability–plasticity is a live sequence-model problem, not a metaphor imported from nowhere.**
   Palimpsa treats attention-based sequence models as continual learners facing a stability–plasticity dilemma and introduces Bayesian metaplasticity so some state components remain more rewritable than others. That gives DelayBasin a serious transformer-facing analogy for why archive surfaces may need different rewrite resistance. ([`REF-0122`](../00-meta/bibliography.md))

4. **Portable memory can be compiled into compact artifacts rather than left entangled with full history or persistent weights.**
   Latent Context Compilation compiles long context into portable buffer tokens while regularizing against manifold collapse. This pressures DelayBasin toward lane discipline: some public surfaces may be best treated as compact portable state, while others remain backing evidence or slow constitutional scaffolds. ([`REF-0123`](../00-meta/bibliography.md))

5. **Persistent memory without selective forgetting can leak across domains and amplify bias.**
   PersistBench finds high failure rates from cross-domain leakage and memory-induced sycophancy when long-term memories persist across sessions. That is strong counterpressure against turning every successful local object into long-lived canon. ([`REF-0124`](../00-meta/bibliography.md))

6. **Benchmarks and architectures keep rediscovering multi-timescale memory splits.**
   BEAM/LIGHT and related hierarchical-memory work separate working memory, episodic memory, and scratchpad-like accumulation; JANUS explicitly selects what to consolidate at different timescales with managed update policies rather than preserving undifferentiated history. This pressures DelayBasin to admit that its own stack already contains fast, medium, and slow surfaces whether or not it names them. ([`REF-0125`](../00-meta/bibliography.md), [`REF-0126`](../00-meta/bibliography.md))

7. **Drift mitigation benefits from consolidation plus anchoring, not only more context.**
   Agent Drift argues that episodic memory consolidation and adaptive anchoring can mitigate long-horizon degradation in multi-agent systems. That is useful pressure for DelayBasin: fast lane objects should not just accumulate; they should either consolidate upward, refresh, or expire. ([`REF-0127`](../00-meta/bibliography.md))

None of this proves that DelayBasin has found the right lane scheme.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin explicitly stratifies surfaces by timescale and names how material moves, cools, or expires between those lanes.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **timescale map**: fast refreshable diagnostic/control surfaces, medium revisable mechanism/promptcraft surfaces, and slow constitutional surfaces, plus explicit transfer rules among them.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has discovered the unique optimal lane map, a literal neural consolidation schedule, or a transformer-native plasticity controller expressed in text.

## Fast lane vs medium lane vs slow lane

To keep this note honest, DelayBasin needs a three-way distinction:

- **Fast lane** — cheap-to-refresh surfaces used for local fidelity, diagnosis, or bounded correction.
  Current examples: sentinel panels, witness panels, identification packets, challenge probes, some hold packets.
- **Medium lane** — revisable project understanding that should learn across sessions but not churn every turn.
  Current examples: method notes, open questions, prompt-pair evolution, many canon claims.
- **Slow lane** — constitutional surfaces whose job is to preserve admissibility law, ids, and recovery discipline.
  Current examples: invariants, move registry, promotion contracts, recovery kernel, core lexicon discipline.

The important point is not the labels themselves.
It is the **transfer rule**:
- some fast-lane material should expire after use,
- some should consolidate upward if it repeatedly proves load-bearing,
- some medium-lane material should cool or demote instead of ossifying,
- and slow-lane surfaces should require explicit promotion/demotion pressure rather than casual local rewrite.

A compact lane map therefore helps DelayBasin ask not only:
- what is true,
- what is the delta,
- what probe should challenge it,

but also:
- **what lane should this object live in?**
- **what would justify moving it to a slower or faster lane?**
- **what should expire rather than consolidate?**
- **what happens if a fast local success is prematurely canonized?**

## Countermodels / probes

1. **Existing-stack-is-enough countermodel**
   - DelayBasin may already encode timescale separation implicitly through claims, invariants, decay patrol, and quarantine, making a new lane term decorative.
   - Probe: compare revisions that only preserve local object type with revisions that explicitly name fast/medium/slow lane and transfer rule; see whether later sessions misplace or over-consolidate fewer objects.

2. **Everything-is-medium countermodel**
   - The archive may be too small to justify explicit lane distinctions; nearly all useful surfaces may just live in one revisable middle band.
   - Probe: inspect whether sentinel, witness, or identification objects actually behave differently from invariants and move law in later revisions.

3. **Lane-label theater countermodel**
   - Lane labels may become prestige bureaucracy rather than improving continuation.
   - Probe: keep the contract minimal — lane plus transfer rule — and check whether that reduces churn or merely adds terminology.

4. **Consolidation-romance countermodel**
   - Periodic consolidation may sound principled but simply rebrand recap or manual curation.
   - Probe: compare explicit lane transfers against ordinary summary edits under equal token budgets and watch whether the former preserves discrimination better.

5. **Metaplasticity-overreach countermodel**
   - The transformer-facing analogy may be too strong; the archive could just be a human governance device with no meaningful relation to model-side plasticity.
   - Probe: keep the public-metaplasticity story quarantined until lane discipline shows disproportionate value across stale reopen, drift, and cross-domain leakage pressure.

## Design consequences

This mechanism frame pressures DelayBasin to do four things more explicitly:
- preserve a compact **lane classification** when a new archive object is materially load-bearing;
- preserve the **transfer rule**: consolidate upward, refresh in place, cool/demote, or expire;
- avoid silently upgrading fast local probes into medium or slow constitutional state without a promotion reason;
- and treat selective forgetting as a legitimate design move rather than a failure of diligence.

A minimal lane annotation can stay very small:
- one lane label,
- one transfer rule,
- and one failure mode if the object is kept too long or moved too early.

This does not require a global ontology rewrite.
It requires admitting that DelayBasin is already operating with hidden timescale assumptions and that leaving them implicit invites both archive bloat and continuity drift.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than “external memory helps”:
**whether a stateless transformer continuation can be stabilized by a user-space public state that carries not only content, but a compact plasticity schedule — which surfaces should refresh quickly, which should consolidate slowly, and which should resist rewrite unless constitutional pressure is present.**

That would matter for transformers.
It would suggest that long-horizon archive method may need not only state packets, innovation packets, sentinels, and identification moves, but also an explicit **timescale stratification** for public control state.

The stronger story — that DelayBasin may be learning a public metaplasticity schedule or text-level fast/slow memory hierarchy for transformer continuation — remains live, but belongs in quarantine for now.
