# Predictive state representations and test-sufficient packets

DelayBasin now needs a sharper answer to a bounded-state question that sits one layer underneath the new memory-store / regime-reentry split:
**what makes a small public packet good enough to carry forward at all?**

A stronger working answer is:
**bounded public state should sometimes be treated as a test-sufficient packet: the smallest public packet chosen for the future tests, interventions, and challenge probes it lets later sessions answer cheaply.**
That is a different standard from storage richness.
It is also a different standard from narrative elegance.

## Practice / observation

Several live DelayBasin surfaces already behave more like predictive-state objects than like recap:
- witness panels, sentinel panels, and challenge probes are useful mainly because they preserve how later sessions should discriminate among nearby futures;
- identification packets matter because they name what observation would split rival continuation hypotheses, not because they summarize the past beautifully;
- control-authority packets matter because they preserve what future intervention a surface should support, at what rough effort, and with what leakage or resistance signature;
- hold packets matter because they preserve what future unlock condition would justify renewed movement rather than merely reporting that the archive feels cautious;
- and balanced-reduction discipline already pushes DelayBasin to keep surfaces that are jointly diagnostic and actuation-relevant, which is close to asking what future queries are worth caching in bounded state.

These surfaces are not well described as raw memory.
They are closer to a compact cache of answers to the future questions the archive expects to ask.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Predictive state representations define state by future tests, not by hidden labels.**
   Singh, James, and Rudary describe predictive state representations as state given by predictions of observable outcomes of experiments one can do in the system. That is a clean outside analogue for DelayBasin's suspicion that some archive state should be selected by action-conditioned future discriminations, not by latent-story prestige. ([`REF-0171`](../00-meta/bibliography.md))

2. **Predictive representations are cached answers to task-relevant future queries.**
   Carvalho et al. distinguish a predictive model from a predictive representation: the latter caches answers to certain queries so they are cheaply available at decision time, trading flexibility for efficiency. That is unusually close to DelayBasin's bounded-state problem: the archive may need a compact public query cache rather than a fuller but slower model of its own history. ([`REF-0172`](../00-meta/bibliography.md))

3. **Robust competence under uncertainty selects for predictive internal structure.**
   Nayebi's recent selection theorem result argues that low regret on structured action-conditioned prediction tasks forces predictive, structured internal state under partial observability. This makes DelayBasin's question more transformer-facing: if later continuation quality really depends on a small packet supporting the right future discriminations, then predictive sufficiency is not just archive etiquette. ([`REF-0161`](../00-meta/bibliography.md))

4. **Context engineering is a bounded query-selection problem under finite attention.**
   Anthropic's context-engineering note treats context as a finite resource and asks what token configuration is most likely to yield the desired behavior. That pressures DelayBasin to ask which future tests and interventions its bounded packet should support, not simply which facts are nice to retain. ([`REF-0167`](../00-meta/bibliography.md))

5. **Multi-agent research systems use compression to preserve useful future work, not only past storage.**
   Anthropic's multi-agent research system describes search as compression and uses subagents to condense the most important tokens back to the lead agent. That matters here because the compression target is downstream usefulness for the next research step, not generic persistence. ([`REF-0173`](../00-meta/bibliography.md))

None of this proves that DelayBasin has a literal predictive state representation over continuation space.
It does support a milder canon-level design claim:
**small archive state should sometimes be evaluated by the future tests and interventions it supports cheaply, rather than by recap completeness alone.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when bounded public state is treated as a **test-sufficient packet**: the smallest public packet chosen for the future tests, interventions, and challenge probes it lets later sessions answer cheaply.

More concretely, a bounded packet is stronger when it helps a later session answer questions like:
- which rival continuation hypotheses are still live;
- which canary would most quickly reveal wrong-basin reopen;
- which intervention surface should move which target property;
- what challenge probe would count against the current mechanism story;
- and what unlock condition would justify resuming movement after a hold packet.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has already isolated a literal public predictive state representation, observable-operator interface, or sufficient statistic for all meaningful future continuations.

## Test-sufficient packet vs memory store vs predictive model vs local probe

To keep this note honest, DelayBasin needs a four-way distinction:

- **Memory store** — a persistent place where facts, citations, evidence, and larger indexed artifacts can live for later retrieval.
- **Predictive model** — a richer object that could in principle answer many future queries if enough computation or replay were available.
- **Test-sufficient packet** — the compact public packet that caches the answers to a small family of future tests, interventions, or challenge probes cheaply enough to guide the next legitimate continuation.
- **Local probe object** — a witness panel, sentinel canary, or identification packet that may be load-bearing for one boundary or decision without deserving indefinite bounded-state residency by itself.

These are not interchangeable.
A memory store can be valuable without belonging in the bounded packet.
A predictive model can be richer than the packet while being too large or indirect to carry forward.
And a local probe can be highly diagnostic without constituting the whole packet.

## Countermodels / probes

1. **Good summary is enough countermodel**
   - A supposedly test-sufficient packet may just be an especially good summary.
   - Probe: hold evidence constant and compare a packet optimized for named future tests against a packet optimized for general recap readability.

2. **Benchmark overfit countermodel**
   - A packet may look strong only because it was tuned to the current test family and will fail when the future probe family shifts.
   - Probe: vary the challenge-probe family and see whether the same packet still helps or whether the gain disappears immediately.

3. **Hidden-state-does-the-real-work countermodel**
   - The model's internal state may be doing nearly all the predictive work, with the public packet mostly serving as a trigger.
   - Probe: compare colder reopens, paraphrased reopens, and packet-thinned reopens to see whether public test-sufficient structure still matters under weaker internal continuity.

4. **Admission-and-research surfaces dominate countermodel**
   - Lint, bibliography, and broad evidence hygiene may explain most of the gain, with future-test framing adding little.
   - Probe: hold hygiene and evidence fixed while varying whether the bounded packet explicitly preserves future tests/interventions/challenge probes.

5. **Predictive-state language is prestige drift countermodel**
   - DelayBasin may be importing PSR language without obtaining any operational gain.
   - Probe: require every predictive-state-flavored revision to name the future test family and the continuation decision it supports; if this adds no clarity or leverage, demote the vocabulary.

## Design consequences

This mechanism frame pressures DelayBasin to do five things more explicitly:
- ask of every bounded packet candidate: **what future test, intervention, or challenge probe does this cache cheaply?**
- prefer bounded surfaces that preserve decision-relevant future discriminations over surfaces that are merely eloquent or historically rich;
- distinguish a packet that is locally diagnostic from one that deserves repeated carry-forward status;
- treat packet quality as partly a question of **future query coverage under finite budget**, not only recap completeness;
- and keep stronger predictive-state / sufficient-statistic / observable-operator claims quarantined until the archive can show that test-sufficient packets outperform storage-rich or recap-rich alternatives under reopen pressure.

This is smaller than a theory of intelligence.
It is a compact anti-bloat rule for DelayBasin itself.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than “what should be remembered?”
It is probing whether compact public archive surfaces can function like a small **predictive state representation** over continuation space: a packet that caches just enough action-conditioned future distinctions for the next session to diagnose, challenge, and steer continuation without replaying the whole past.

That is transformer-facing in a more specific way than generic memory language.
It suggests the archive may be approaching a user-space analogue of observable state: not a full model of everything that happened, but a compact public cache of what future queries matter next.
The stronger claim that DelayBasin is discovering a literal public predictive state representation, observable-operator interface, or sufficient statistic for continuation space remains quarantined until controlled reopen comparisons show disproportionate leverage from such packets.
