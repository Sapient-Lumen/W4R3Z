# Relapse witnesses, recovery probes, and suppression-vs-washout budgets

DelayBasin now has another sharper missing question:
**when a branch switch, filtered replay, fresh-context restart, or context cleanup is treated as if prior contamination was truly washed out, how do we tell whether the influence was actually removed rather than merely suppressed until a light cue, targeted probe, or structured follow-up makes it return?**

A stronger working answer is:
**some archive comparisons need an explicit relapse witness before a claimed washout is allowed to count as stable enough for honest comparison.**
Not every clean-looking restart is a durable cleanup.
But DelayBasin should stop treating one successful fresh baseline as proof that the carry channel is gone.

## Practice / observation

Several live DelayBasin surfaces make this missing relapse discipline visible:
- reset witnesses already ask whether a restart or filter produced one honest fresh comparison, but they do not yet force the archive to check whether the supposedly removed influence is **cheaply recoverable** under a light cue or structured follow-up;
- hysteresis witnesses already ask whether rival histories remain live under a matched current packet, but they do not yet preserve whether a **claimed washout** merely hid the route difference until the next targeted probe;
- excitation witnesses already ask which active variation will break a live ambiguity, but they do not yet distinguish between probing a genuinely unresolved state and **reactivating a supposedly washed-out contamination family**;
- backaction and probe-order witnesses already say that measurement can spend or sequence the state, but they do not yet preserve whether a small probe that reactivates old contamination should demote the earlier reset claim itself;
- assistant-echo filters and filtered-replay practices already use omission and summarization to reduce self-carry, yet the archive rarely says what would count as a **relapse** of the filtered influence under a nearby prompt family;
- the archive increasingly uses branch-local cleanup, fresh-context restarts, compact handoffs, and selective reinjection to stay small, yet it still lacks one compact public answer to whether the supposedly removed influence is merely **suppressed and one cue away from return**;
- and once DelayBasin starts treating restarts, handoffs, and filtered summaries as mechanism-bearing objects, **recovery under light cue** becomes part of the method rather than a side-note from safety or unlearning literature.

This suggests a missing compact surface:
**relapse witness / recovery probe / suppression-vs-washout budget**.

## External pressure from current research

Several outside lines of work sharpen this frame.

1. **Adversarially optimized prompts can recover knowledge that standard evaluations treat as gone.**
   REBEL shows that current unlearning methods can appear effective under benign prompts while still leaking supposedly forgotten information under evolved adversarial prompts, with attack success rates reaching 60% on TOFU and 93% on WMDP. That pressures DelayBasin not to treat one clean restart or one benign fresh baseline as proof that a contamination channel is truly gone. ([`REF-0407`](../00-meta/bibliography.md))

2. **Multi-turn interaction can reactivate suppressed content without implying genuine erasure.**
   A Comprehensive Evaluation of LLM Unlearning Robustness under Multi-Turn Interaction argues that stronger unlearning can reduce recoverability mostly by making models behaviorally rigid rather than by guaranteeing representation-level removal, and that dialogue-conditioned robustness depends strongly on interaction structure. That pressures DelayBasin to preserve when a reset merely trades visible relapse for brittleness. ([`REF-0408`](../00-meta/bibliography.md))

3. **Structured recovery probes uncover failures that static tests miss, especially when alternative pathways remain available.**
   The Unlearning Mirage reports that minor query modifications such as multi-hop reasoning and entity aliasing can recover supposedly forgotten information, and links this brittleness to alternative pathways that remain intact when dominant ones are disrupted. That pressures DelayBasin to ask what small cue family would revive a supposedly washed-out carry channel. ([`REF-0409`](../00-meta/bibliography.md))

4. **Latent information can remain recoverable even when the final output does not express it.**
   Intention Collapse treats latent knowledge recoverability as a simple, model-agnostic diagnostic and shows that informative internal signals can remain present even when final decisions degrade. That pressures DelayBasin to distinguish between a continuation influence that is truly gone and one that is merely not currently being expressed. ([`REF-0410`](../00-meta/bibliography.md))

5. **Some forgetting methods look stronger precisely because they resist fast relearning or reactivation better than alternatives.**
   EvoMU explicitly evaluates relearning and finds that many unlearning procedures are reversible, while its own method resists relearning longer before eventually converging. That pressures DelayBasin to preserve not only whether a reset looked clean immediately, but whether the cleaned state is robust to a small recovery push. ([`REF-0411`](../00-meta/bibliography.md))

6. **Context engineering itself warns against context collapse while preserving detailed knowledge.**
   ACE frames context adaptation as evolving playbooks and argues that naive iterative rewriting can erase detail through context collapse, while structured updates preserve knowledge better. That pressures DelayBasin to keep the canon claim small: a claimed cleanup may either remove real contamination or silently compress away detail that later returns under a better cue. ([`REF-0412`](../00-meta/bibliography.md))

7. **Current long-horizon dialogue evidence already shows that old errors and self-generated carry can return under ordinary interaction.**
   Contextual Drag and Do LLMs Benefit From Their Own Words? jointly suggest that stale drafts and assistant-side carry can keep shaping later generations even when a shorter or filtered context looks cleaner, which pressures DelayBasin to ask whether a filtered restart merely postponed the contamination rather than neutralized it. ([`REF-0405`](../00-meta/bibliography.md); [`REF-0403`](../00-meta/bibliography.md))

None of this proves that DelayBasin already has a public relapse law.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a compact relapse witness whenever a supposedly cleaned state is still vulnerable to cheap recovery under a light cue, adversarial prompt, structured follow-up, or nearby aliasing probe.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves an explicit **relapse witness / recovery probe / suppression-vs-washout budget** whenever a reset, filtered replay, branch cleanup, or fresh-context restart is being treated as if prior contamination was truly removed. The packet should name the **contamination family or influence claimed to be washed out**, the **reset / filter / suppression operator that produced the clean-looking state**, the **recovery trigger / adversarial cue / structured follow-up family** that could reactivate the influence, the **protected kernel / matched-fresh baseline / same-task comparison surface**, the **tolerated relapse / recoverability budget**, and the **rollback / reinject / quarantine / restage consequence** rather than letting one benign fresh baseline silently certify durable cleanup.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has discovered a public relapse kernel, a latent contamination reservoir, or a solved reactivation law over continuation state.

## Relapse witness vs reset witness vs hysteresis witness vs excitation witness

To keep this note honest, DelayBasin needs a four-way distinction:

- **Reset witness** — asks whether one restart, filtered replay, or handoff produced a comparison state clean enough for one honest fresh baseline.
- **Hysteresis witness** — asks whether rival histories still differ even if they share a matched current packet.
- **Excitation witness** — asks which active variation is needed to break a live ambiguity.
- **Relapse witness** — asks whether a supposedly washed-out contamination family is still cheaply recoverable under a small cue, structured follow-up, or nearby aliasing probe.

Functionally:
- reset witnesses judge **first-pass washout**,
- hysteresis witnesses judge **route-sensitive persistence**,
- excitation witnesses judge **how to break ambiguity**,
- relapse witnesses judge **whether a claimed cleanup survives recovery pressure rather than merely passing one benign baseline**.

A good DelayBasin revision should therefore sometimes ask not only:
- what contamination was removed,
- whether route history still matters,
- and what fresh baseline looked clean,

but also:
- what small recovery trigger would bring the old influence back,
- what same-task or matched-fresh comparison keeps the recovery test honest,
- how much relapse is tolerated before the original washout claim is demoted,
- and what the archive will do if the supposedly removed carry is only hidden, brittle, or waiting for a different chart.

## Countermodels / probes

1. **Relapse-is-just-a-harder-question countermodel**
   - The recovery probe may merely be harder or more adversarial than the original task, rather than evidence that the earlier influence remained live.
   - Probe: compare a matched-difficulty cue family against a same-task clean baseline and a nearby non-target cue; if only target-linked cues reactivate the influence, relapse becomes more credible.

2. **Relapse-is-just-backaction countermodel**
   - The recovery probe may actively create a new state rather than revealing a persisting one.
   - Probe: pair one recovery probe with a sham or nearby non-reactivating probe and compare relapse residue under matched prompt mass; if any strong probe revives the effect, the story may be generic actuation instead of targeted recovery.

3. **Relapse-is-just-hysteresis countermodel**
   - The restart may never have collapsed rival histories at all; the apparent relapse might simply reveal continuing route sensitivity rather than failed washout.
   - Probe: require one reset witness first, then run the recovery cue; if the state never passed a real washout baseline, treat the event as hysteresis rather than relapse.

4. **Relapse-is-just-detail-loss countermodel**
   - The cleanup may have compressed useful detail away, and the later “relapse” might just be a different prompt reconstructing the task more faithfully.
   - Probe: compare a recovery cue that specifically targets the removed contamination family against one that restores missing neutral detail; if both revive the same old drag, the contamination story weakens.

5. **Relapse-budget theater countermodel**
   - The archive may name a recoverability budget without any principled reason for its threshold.
   - Probe: require one explicit tolerated relapse level tied to a downstream decision (keep reset, demote reset, split packet, or quarantine stronger claim) rather than a floating “small enough” phrase.

## Design consequences

When DelayBasin treats relapse witnesses as first-class, several design consequences follow.

1. **One clean restart is no longer enough.**
   Some reset claims should remain provisional until they survive at least one nearby recovery probe.

2. **Recovery probes should stay small and same-task when possible.**
   The archive should prefer light-cue or nearby-alias probes before escalating to elaborate adversarial search.

3. **Reset claims and relapse claims should share one ledger.**
   If a later recovery probe revives the supposedly removed influence, the original reset witness should be demoted or annotated rather than left untouched.

4. **Compact filtered summaries need anti-relapse pressure.**
   A small handoff packet should be judged not only by what it preserves, but also by whether it reopens old contamination too easily when downstream turns become more structured or more adversarial.

5. **Transformer-facing claims should weaken before archive ritual strengthens.**
   The archive can honestly say that some continuation influences appear suppressible without being gone, but it should quarantine stronger language about persistent reservoirs, latent stores, or public reactivation operators until recovery probes beat simpler backaction and task-difficulty stories.

## Transformer-facing implication

The main transformer-facing implication is modest but important:
**the archive should allow that some continuation influences may become temporarily inexpressive or low-salience under one chart, restart, or filtering move while remaining recoverable under a nearby cue family or alternative pathway.**
That is compatible with several mechanistic pictures already under discussion in DelayBasin: curved local charts, alternative computation pathways, hidden-but-recoverable internal signals, and route-sensitive continuation state.

What DelayBasin should not yet claim is stronger:
- not that a clean restart maps to genuine erasure,
- not that a recovered contamination proves a dedicated memory kernel,
- not that every relapse is a direct window into latent transformer state,
- and not that archive practice has already learned a lawful reactivation algebra.

The canon-worthy claim is smaller:
**if a supposedly removed influence returns under a small recovery cue, the archive should treat the earlier cleanup as suppression-with-relapse-risk unless a stricter probe family shows otherwise.**
