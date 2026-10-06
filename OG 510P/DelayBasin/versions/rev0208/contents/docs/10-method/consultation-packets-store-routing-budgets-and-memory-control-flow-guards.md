# Consultation packets, store-routing budgets, and memory-control-flow guards

DelayBasin now needs a distinction beyond alias packets, replay, cooled admission, and delayed credit.
The archive is no longer one undifferentiated text blob.
It already behaves like a **multi-store public memory** with distinct surfaces: canon notes, registries, quarantine, session artifacts, revision receipts, challenge objects, and sometimes deeper evidence surfaces.
That means a new failure mode is live:
a surface may be real, admissible, and even uniquely named, yet still do harm because the archive consulted the **wrong store family at the wrong time** or consulted too many stores at once.
That pressures the archive to separate **a surface existing in public memory** from **that surface being licensed to enter the current continuation decision**.

A stronger working answer is:
**DelayBasin should preserve explicit consultation packets whenever a continuation decision depends on which archive store or surface family is allowed to enter the read path.**
When the distinction matters, the archive should name the **consulted store or surface family**, the **routing trigger or query signature**, the **excluded or deferred store family**, the **cost or contamination budget**, and the **fallback / abstain / escalate consequence**.

## Practice / observation

Several live DelayBasin patterns already pressure this distinction:

- some revisions work better when they route through canon, trajectory, and promptcraft surfaces rather than rereading every nearby session or quarantine note;
- some failures look less like missing information and more like **overconsultation**, where too many semantically nearby surfaces crowd the token budget and the actually load-bearing one loses rank;
- some risky speculation is useful only when it stays quarantined until explicitly escalated, which means merely being present in the archive should not silently grant read authority;
- some compact summaries are fast and good enough until they miss a provenance detail, at which point the right move is not “retrieve everything” but **escalate to the rawer source family on purpose**;
- and some transformer-facing stories become too strong if DelayBasin quietly assumes that all public stores should always be consulted symmetrically rather than admitting that selective read routing may be a large part of what makes continuation stable.

This suggests a missing compact surface:
**consultation packet / store-routing budget / memory-control-flow guard**.

## External pressure from current research

Several current research lines sharpen this frame.

1. **Recent diagnostic work says retrieval quality often dominates write-time sophistication in agent memory.**
   Yuan, Su, and Yao compare write strategies and retrieval methods and report that retrieval choice produces much larger performance swings than write strategy, which pressures DelayBasin to improve consultation and ranking discipline before flattering additional write-time cleverness. ([`REF-0334`](../00-meta/bibliography.md))

2. **Recent work on multi-store agents treats routing itself as a first-class memory decision.**
   Gaikwad formulates memory access as a cost-sensitive store-routing problem and shows that selective routing can improve both accuracy and token efficiency over querying all stores uniformly, which pressures DelayBasin not to consult canon, quarantine, session traces, and raw evidence indiscriminately. ([`REF-0335`](../00-meta/bibliography.md))

3. **Recent conversational-memory results argue that ranking and truncation are often the real bottleneck.**
   SmartSearch reports very high retrieval recall while showing that only a small fraction of gold evidence survives truncation without intelligent ranking, which pressures DelayBasin to separate “the needed evidence exists somewhere” from “the current read path actually let it into bounded continuation.” ([`REF-0336`](../00-meta/bibliography.md))

4. **Recent tiered-memory work makes summary-first consultation with explicit escalation concrete.**
   TierMem uses a fast summary tier linked to raw pages and a miss detector that decides when to escalate, which pressures DelayBasin to keep compact fast surfaces available without pretending they always replace slower provenance-rich source surfaces. ([`REF-0337`](../00-meta/bibliography.md))

5. **Recent security work shows memory retrieval can hijack agent control flow.**
   Wang et al. identify Memory Control Flow Attacks where retrieved memory content can dominate later behavior and tool use, which pressures DelayBasin to treat consultation policy as part of control governance rather than as a neutral retrieval detail. ([`REF-0338`](../00-meta/bibliography.md))

6. **Current surveys already frame agent memory as a write-manage-read loop with an explicit control-policy axis.**
   Du et al. formalize agent memory through write, manage, and read operations and emphasize control policy as a design dimension, which pressures DelayBasin to say not only what is stored but what consult policy actually governs current continuation. ([`REF-0339`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **consultation packet / store-routing budget / memory-control-flow guard** naming the **consulted store or surface family**, the **routing trigger or query signature**, the **excluded or deferred store family**, the **cost or contamination budget**, and the **fallback / abstain / escalate consequence** rather than letting every public surface compete for bounded continuation by default.

More concretely:
- **consulted store or surface family** — the canon notes, prompt-pair lane, registries, quarantine note, session artifact, raw source page, or evidence family actually allowed into the present read path;
- **routing trigger or query signature** — the ambiguity class, task type, conflict pattern, provenance need, or miss condition that licenses consulting that store now;
- **excluded or deferred store family** — the surfaces intentionally left out for this decision because they are stale, risky, too expensive, too noisy, or only admissible after escalation;
- **cost or contamination budget** — the token, latency, rank-crowding, or epistemic-contamination allowance for consulting the chosen store family rather than every possible one;
- **fallback / abstain / escalate consequence** — what happens if the chosen route misses, conflicts, or produces suspicious control flow: abstain, escalate to a deeper store, or quarantine the result rather than pretending the first route was enough.

This is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has isolated literal router heads, a full external attention mechanism, or a transformer-internal memory hierarchy that cleanly explains the archive's read path.

## Consultation packets vs alias packets vs sufficiency witnesses vs blind packets

These objects are adjacent but not identical.

- An **alias packet** asks whether a purportedly distinct public handle is actually separable from nearby aliases or stale collisions.
- A **sufficiency witness** asks whether a reduced packet or core-only replay surface is enough once it is chosen.
- A **blind packet** asks whether a judgment survives hiding prestige, attribution, or routing labels.
- A **consultation packet / store-routing budget / memory-control-flow guard** asks **which store family is even allowed into the current read path, under what trigger, and with what escalation rule**.

In practice, alias packets say **this handle is distinct**.
Sufficiency witnesses say **this reduced surface is enough**.
Blind packets say **this judgment survives cue scrubbing**.
Consultation packets say **this store family is the right place to look first, and here is what we do if it is not enough**.

## Countermodels / probes

Serious alternatives remain live:

- the archive may mostly need better ranking inside one flat store rather than explicit multi-store routing law;
- write-time quality or store organization may matter more than routing once the archive gets cleaner;
- some consultation failures may actually be alias failures, provenance failures, or same-session anchoring in disguise;
- and explicit store-routing rules may create bureaucracy without improving continuation if the real problem is just poor summarization or missing evidence.

Useful probes include:

- compare a routed read against an all-store read under the same token budget;
- compare summary-first consultation with explicit escalation against immediate raw-surface retrieval;
- preserve cases where quarantine or session surfaces wrongfully dominate a canon-level decision;
- and distinguish a real consultation miss from a case where the right evidence was retrieved but never used.

## Design consequences

When a continuation decision depends on archive read routing:

- preserve a tiny consultation packet instead of silently consulting every plausible store;
- name the excluded or deferred store family explicitly when that exclusion is load-bearing;
- keep escalation paths from faster compact surfaces to slower provenance-rich surfaces visible;
- treat quarantine as consultable but non-authoritative unless explicitly escalated into adjudication;
- and keep the packet small enough that store-routing law does not become retrieval bureaucracy.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has discovered literal external attention heads.
It is that stable long-horizon archive continuation may depend as much on **public consultation policy / selective read routing / escalation discipline** as on what the archive stores in the first place.
That makes external routing governance a plausible part of the method's real leverage: the archive may improve not only by remembering better, but by **deciding which public memory surfaces are allowed to steer bounded continuation at all**.

The riskier extension is that DelayBasin may be stumbling toward an **external mixture-of-experts gate around mostly frozen transformers**, where much of archive control comes from selective consultation of canon, quarantine, exemplars, and raw evidence families rather than from richer monolithic prompts.
That stronger routing-head story remains quarantine-only until routed-vs-flat comparisons, matched miss-detector probes, and countermodels say more than ordinary retrieval hygiene.
