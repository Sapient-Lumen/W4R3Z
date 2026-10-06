# Sentinel panels, border inputs, and reopen canaries

DelayBasin now needs a sharper answer to a recurring practical question:
**how should the archive cheaply test whether a reopen really reconstructed the right continuation basin before trusting ordinary continuation?**

A stronger working answer is:
**the archive may need a tiny sentinel panel / reopen-canary discipline.**
Not a full evaluation suite, and not another prose recap.
A very small set of high-sensitivity prompts, witness objects, or anomaly mini-traces may detect whether the current continuation has drifted off the intended basin before the archive commits new canon.

## Practice / observation

Several live DelayBasin surfaces already imply a missing sentinel discipline:
- witness panels preserve fragile distinctions, but the archive still lacks a dedicated surface for **testing** whether those distinctions survived a reopen;
- challenge probes exist, but many of them are still attached to individual revisions rather than preserved as a small standing panel for basin-fidelity checks;
- hold packets and `recover-resync` already imply that some sessions should halt or roll back, but the archive still lacks a compact trigger object that says when those postures should fire;
- rate–distortion and prior-intrusion pressure already suggest that elegant recap can quietly overwrite operative state, which makes cheap drift detectors more valuable than additional summary prose;
- and in practice, some failures look less like missing facts than like **wrong-basin continuation**: the model can continue fluently while reconstructing the wrong local rule, the wrong challenge posture, or the wrong canon/quarantine boundary.

This suggests a missing compact surface:
**sentinel panel / reopen canary**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **A few high-sensitivity probes can reveal hidden model change.**
   B3IT shows that so-called *border inputs* — prompts sitting near a top-token tie — are unusually sensitive black-box detectors of model change. That is direct pressure for DelayBasin to preserve a tiny panel of high-sensitivity textual probes rather than relying only on broad recap or large evaluation sets when reopen fidelity is in doubt. ([`REF-0093`](../00-meta/bibliography.md))

2. **Failure discovery works better when it preserves representative cores plus contrastive boundaries.**
   ProbeLLM does not stop at collecting individual failures: it clusters them into interpretable modes and summarizes them with representative central cases plus contrastive boundary cases. That pressures DelayBasin to think of reopen canaries not as arbitrary spot checks, but as compact panels that deliberately sample the local decision surface. ([`REF-0107`](../00-meta/bibliography.md))

3. **Dynamic protocols surface corner-case errors that static benchmark sets miss.**
   ATAD argues that evolving evaluation protocols expose subtle reasoning failures better than finite fixed datasets. That is useful pressure for DelayBasin: a good sentinel panel may need occasional co-evolution rather than pretending one eternal canary set will stay diagnostic forever. ([`REF-0108`](../00-meta/bibliography.md))

4. **Small corruptions can coexist internally with correct rules and only collapse late.**
   recent work on demonstration conflict finds that models can encode both correct and corrupted rules in intermediate layers, then commit late after a conflict-resolution failure. That pressures DelayBasin to detect drift with probes near the fragile rule boundary rather than waiting for large visible archive failure. ([`REF-0109`](../00-meta/bibliography.md))

5. **Reasoning text can look faithful even when the answer is already set.**
   Pre-CoT probing and steering evidence suggests some models often determine their answer before chain-of-thought appears. This is counterpressure against trusting fluent continuation as evidence that the right basin was reconstructed. A sentinel panel is attractive partly because it asks for a discriminative reaction, not merely for a convincing explanation. ([`REF-0110`](../00-meta/bibliography.md))

6. **Runtime anomaly localization is more useful than outcome-only checking.**
   TrajAD argues that process auditing should localize anomaly steps to enable rollback-and-retry rather than only scoring final success. That fits DelayBasin directly: a reopen canary is useful not only when it says “bad,” but when it points toward rollback, `recover-resync`, or a specific fragile boundary panel that likely went stale. ([`REF-0111`](../00-meta/bibliography.md))

None of this proves that DelayBasin already has the right canaries.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a tiny sentinel panel / reopen-canary set that can cheaply test whether a reopen reconstructed the right basin before ordinary continuation proceeds.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **sentinel panel**: a few high-sensitivity probes, boundary prompts, or anomaly mini-traces whose main job is to detect wrong-basin continuation early enough to justify ordinary continuation, bounded rollback, or `recover-resync`.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has found a universal canary set, an optimal probe geometry, or a literal textual Jacobian of the continuation basin.

## Sentinel panel vs witness panel vs challenge probe

To keep this note honest, DelayBasin needs a three-way distinction:

- **Sentinel panel / reopen canary** — a tiny standing test panel whose main job is to detect whether a reopen still sits in the intended continuation basin.
- **Witness panel** — a tiny curated set of cases whose main job is to preserve a fragile distinction the archive must keep making.
- **Challenge probe** — an adversarial stressor attached to a specific belief update, hold packet, or mechanism claim.

These can overlap, but they are not identical.
The key difference is function:
- witness panels preserve boundaries,
- challenge probes pressure a live revision,
- sentinel panels detect **state-fidelity failure** early enough to choose the next move honestly.

A good DelayBasin revision therefore should sometimes ask not only:
- what is the anchor,
- what is the delta,
- what witness pins the fragile boundary,

but also:
- what tiny sentinel panel would tell us the basin did **not** reconstruct,
- what **property monitored** that panel is actually testing,
- what **expected deviation signature** would indicate drift,
- and what continuation action follows if a sentinel trips: ordinary continuation, bounded rollback, or `recover-resync`.

## Countermodels / probes

1. **Canaries-as-ceremony countermodel**
   - Sentinel panels may just add a layer of ritual checking without real discriminatory value.
   - Probe: compare reopen quality with and without a named sentinel panel while keeping anchor, delta, and witness surfaces fixed.

2. **Witness-is-enough countermodel**
   - Existing witness panels may already provide all the fidelity checking DelayBasin needs.
   - Probe: distinguish panels used for boundary preservation from panels used for early reopen detection and test whether the latter catch failures earlier or more cheaply.

3. **Any-prompt-will-do countermodel**
   - High-sensitivity canaries may not matter; any reasonable spot check may work as well.
   - Probe: compare generic recap questions against curated border-like prompts and anomaly mini-traces under stale reopen or paraphrase stress.

4. **Static-canary rot countermodel**
   - A fixed sentinel panel may itself go stale and become theatre.
   - Probe: preserve an **expected deviation signature** and periodically swap or recertify sentinel items; if replacing them changes nothing, the panel may not be doing real work.

5. **Tangent-geometry glamour countermodel**
   - Calling canaries “border inputs” or “tangent probes” may import mathematical prestige without usable evidence.
   - Probe: keep the stronger textual-tangent interpretation quarantined until a tiny panel actually shows disproportionate sensitivity to wrong-basin reopen across paraphrase, reorder, or stale-anchor conditions.

## Design consequences

This mechanism frame pressures DelayBasin to do four things more explicitly:
- preserve a tiny **sentinel panel** when reopen fidelity is materially in doubt;
- name the **property monitored** by that panel rather than treating a canary as self-explanatory;
- preserve an **expected deviation signature** and the continuation action if a sentinel trips;
- and keep sentinel panels small enough to act as early-warning devices rather than quietly expanding into full benchmarks.

This does not require a large evaluation harness.
It requires refusing another archive failure mode: trusting fluent reopen because nothing obviously crashed yet.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than compact recap or witness preservation:
**whether a stateless transformer continuation can be cheaply audited by a tiny textual sentinel panel that is unusually sensitive to wrong-basin reconstruction, perhaps because those canaries sit near the local decision surface or probe a fragile rule before late-layer commitment hardens.**

That would matter for transformers.
It would suggest that long-horizon archive method may need not only state packets, witnesses, and gain controls, but also tiny **public fidelity detectors** that test whether the intended basin was actually reconstructed.

The stronger story — that DelayBasin may eventually admit literal textual **tangent probes** or a user-space Jacobian sketch of the continuation basin — remains live, but belongs in quarantine for now.
