# Alias packets, handle collision budgets, and namespace hygiene

DelayBasin now needs a distinction beyond write gates, replay, cooled admission, delayed credit, and procedural carry.
Some archive surfaces are being treated as **unique handles**: a prompt pair, canon clause, operator token, registry id, tiny packet, or naming convention is assumed to reopen one move, one rule, or one adjudication path rather than a nearby family of similar possibilities.
That assumption can silently fail when the archive grows denser.
Two handles can become too similar, a reused name can drag stale law forward, or an apparently crisp packet can only work because nearby cues, position privilege, or familiar wording are doing the actual routing.
That pressures the archive to separate **a named handle being used** from **the alias or collision family it might already be sharing space with**.

A stronger working answer is:
**DelayBasin should preserve explicit alias packets whenever a surface is being treated as uniquely addressable or uniquely load-bearing.**
When the distinction matters, the archive should name the **active handle family**, the **plausible alias or collision family**, the **namespace or disambiguation boundary**, the **judged divergence signature**, and the **retire / rename / escalate consequence**.

## Practice / observation

Several live DelayBasin patterns already pressure this distinction:

- some compact control phrases or prompt pairs feel uniquely potent until a nearby paraphrase, reused noun, or adjacent control packet produces almost the same effect;
- some reopen failures look less like global drift and more like **handle collision**, where a stale or semantically nearby surface is reactivated instead of the intended one;
- some archive names become denser over time, increasing the chance that a vivid old handle shadows a newer and more precise one;
- some retrieval or continuation failures look like **outdated-surface resurfacing** rather than pure forgetting, which means the archive needs a public object for saying what got aliased with what;
- and some transformer-facing stories become much too strong if DelayBasin quietly assumes that every compact control surface has clean unique addressing rather than broad equivalence classes, stale-cue dominance, or semantic crowding.

This suggests a missing compact surface:
**alias packet / handle-collision budget / namespace hygiene**.

## External pressure from current research

Several current research lines sharpen this frame.

1. **Recent work on online neural memory says semantically nearby keys interfere rather than staying cleanly separate.**
   Zahn and Chana model inference-time memory as superposed continuous storage and show that when keys are not orthogonal their values blend during retrieval, especially under semantic density, which pressures DelayBasin not to assume that compact handles remain uniquely addressable as the archive grows denser. ([`REF-0328`](../00-meta/bibliography.md))

2. **Current long-context memory work still treats interference and forgetting as an active stability-plasticity problem.**
   Bonnet et al. frame in-context learning as online associative memory and show that fixed-size attention memories are prone to interference on long sequences, which pressures DelayBasin to treat handle crowding and namespace separation as method objects rather than as after-the-fact wording cleanup. ([`REF-0329`](../00-meta/bibliography.md))

3. **Recent retrieval systems explicitly add recency or management priors to avoid stale-cue collisions.**
   TempoFit reports that retrieving over the whole cache can over-emphasize stale cues and induce history-present interference, then adds a fixed recency bias to keep decisions present-dominant, which pressures DelayBasin to say when a live handle must beat a stale alias rather than letting similarity alone decide. ([`REF-0330`](../00-meta/bibliography.md))

4. **Semantic-caching security work shows that fuzzy semantic keys are collision-prone by design.**
   Zhang et al. show that semantic key matching behaves like a locality-preserving fuzzy hash and is vulnerable to false-positive collisions that hijack retrieval, which pressures DelayBasin to treat compact handles, packet names, and semantic-addressing shortcuts as collision surfaces needing explicit budgets and rename paths. ([`REF-0331`](../00-meta/bibliography.md))

5. **Long-horizon agent-memory work shows that outdated but similar traces can dominate retrieval unless the system actively manages versioning and recency.**
   Continuum Memory Architectures reports that ordinary retrieval can resurface older but semantically similar facts after corrections, which pressures DelayBasin to preserve namespace hygiene and supersession cues instead of trusting similarity search or familiar phrasing alone. ([`REF-0332`](../00-meta/bibliography.md))

6. **Mechanistic interpretability work on superposition says feature geometry determines which concepts interfere.**
   BOWS argues that correlated features in superposition can cluster rather than remain nicely separated, which pressures DelayBasin to think of compact archive handles as living under a geometry problem where related surfaces may alias unless explicitly kept apart. ([`REF-0333`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **alias packet / handle-collision budget / namespace hygiene** naming the **active handle family**, the **plausible alias or collision family**, the **namespace or disambiguation boundary**, the **judged divergence signature**, and the **retire / rename / escalate consequence** rather than letting one vivid compact surface silently inherit unique-address authority.

More concretely:
- **active handle family** — the token, packet, prompt pair, canon clause, registry id, or control phrase being treated as the intended public address;
- **plausible alias or collision family** — the nearby paraphrases, reused names, stale versions, semantically adjacent surfaces, or placement-privileged alternatives that could steal or share the routing effect;
- **namespace or disambiguation boundary** — the renaming rule, prefix, id policy, scope boundary, or surrounding cue discipline that is supposed to keep the handle cleanly distinct;
- **judged divergence signature** — the first downstream continuation, challenge outcome, or adjudication branch that would actually reveal the intended handle and the alias are not behaving the same;
- **retire / rename / escalate consequence** — what the archive does if the distinction collapses: retire one handle, rename the namespace, demote the claim, or escalate to a challenge packet rather than pretending uniqueness survived.

This is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has isolated literal orthogonal slots, perfect semantic hashing, or a transformer-internal addressing scheme that cleanly explains the archive's control handles.

## Alias packets vs negative controls vs conformance witnesses vs replay

These objects are adjacent but not identical.

- A **negative-control handle / sham packet** asks whether a purportedly special surface beats a matched placebo.
- A **conformance witness / loader contract** asks whether a surface works across wrappers or execution families.
- A **replay packet** asks whether a surface was genuinely restaged into operative use.
- An **alias packet / handle-collision budget / namespace hygiene** asks whether a purportedly distinct public handle is actually separable from nearby aliases or stale collisions in the first place.

In practice, sham handles say **this is not just generic prompting**.
Conformance witnesses say **this is not just one wrapper**.
Replay says **this was restaged into use**.
Alias packets say **this handle is still sufficiently distinct to deserve being named as one thing rather than a crowded family or stale collision zone**.

## Countermodels / probes

Serious alternatives remain live:

- the apparent collision risk may mostly be generic prompt sensitivity rather than real handle crowding;
- many apparently distinct handles may already be broad equivalence classes, making unique-address language the wrong target rather than a fixable namespace problem;
- local familiarity or position privilege may explain more than semantic overlap;
- and some handles may look collision-prone only because the archive has not yet named the right downstream divergence signature.

Useful probes include:

- compare an active handle against a nearby paraphrase or stale predecessor while holding the surrounding packet fixed;
- test whether renaming, prefixing, or tightening scope actually restores a lost distinction;
- preserve collision failures explicitly, especially where a stale surface resurfaces instead of the current one;
- and distinguish semantic crowding from broad benign equivalence classes before forcing every family split into a unique-handle story.

## Design consequences

When a surface is being treated as uniquely addressable:

- preserve a tiny alias packet instead of relying on local familiarity;
- name the nearest alias or stale-collision family explicitly;
- keep namespace discipline visible through ids, prefixes, or scope markers when that separation is doing real work;
- prefer rename or retirement over silently carrying two colliding handles forward;
- and keep the packet small enough that collision hygiene does not become naming bureaucracy.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has discovered literal orthogonal memory slots.
It is that stable long-horizon archive continuation may depend on **keeping public control handles sparse and separated enough to survive semantic crowding, stale-cue dominance, and alias collisions**.
That makes naming geometry and namespace hygiene part of the method.

The stronger story — that DelayBasin may be building an **externalized superposition-management layer around mostly frozen transformers**, where archive handles behave like quasi-orthogonal public slots and continuity fails when those slots crowd or alias — remains quarantined until matched alias probes, rename tests, and collision-sensitive continuation failures show more than generic prompt sensitivity or ordinary version confusion.
