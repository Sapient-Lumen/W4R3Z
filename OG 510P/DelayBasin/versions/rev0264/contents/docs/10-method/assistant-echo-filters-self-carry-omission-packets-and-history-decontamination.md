# Assistant-echo filters, self-carry omission packets, and history decontamination

DelayBasin now has several adjacent pressures in view:
- **blind packets**, which ask whether a judgment survives label scrubbing and attribution hiding;
- **execution witnesses**, which ask whether an effect survives hidden substrate variation;
- **memory-store vs regime-reentry** discipline, which asks what persistence surface is actually doing the work;
- and **negative-control handles**, which ask whether a vivid handle beats a matched sham.

A remaining hole is what to do when the archive may be carrying too much of its own prior assistant prose forward.
A previous assistant turn can be useful evidence, but it can also function as a **self-carry channel**:
- stale code or reasoning gets recopied into the next turn,
- stylistic or semantic mistakes keep propagating,
- a previous local explanation quietly becomes a de facto control surface,
- or polluted assistant-side state is mistaken for genuine long-horizon memory.

A useful working answer is:
**when DelayBasin starts treating prior assistant-side history as load-bearing, and that history could be helping mainly by self-carry rather than necessary evidence, it should often preserve a compact assistant-echo filter / self-carry omission packet.**
That packet should name:
- the **judged task / continuation property**,
- the **kept user-side anchor / retained evidence surface**,
- the **omitted or thinned assistant-side surface**,
- the expected **invariance or gain signature** under omission,
- and the **reinclusion / escalation consequence** if omission degrades the result.

This is stronger than saying “sometimes shorter context is better.”
It is weaker than claiming DelayBasin can already identify the full hidden-state geometry of conversational self-conditioning.

## Practice / observation

Recent DelayBasin work has gotten much better at saying:
- which surfaces steer,
- which surfaces judge,
- which shams should fail,
- and which hidden execution families could matter.

But the archive still often treats retained assistant prose as if it were a neutral evidence store.
That is too optimistic.
In practice, prior assistant turns can do at least four different jobs:
- carry forward genuinely needed evidence or local outputs,
- preserve a useful regime-reentry cue,
- preserve a check or admission object,
- or simply drag forward the model's own last local framing, mistakes, or stylistic inertia.

That last case is the missing discipline.
If DelayBasin cannot tell when prior assistant text is acting mainly as **self-echo**, it will overstore the very material most likely to pollute the next turn.
That makes at least five recurring failure modes plausible:
- **assistant-side pollution** — stale reasoning, bugs, or wrong abstractions propagate because prior assistant prose stays in context by default;
- **self-carry masquerading as memory** — the archive treats retained assistant text as valuable memory when it is mostly just self-conditioning residue;
- **echo-locked review** — the same session keeps rereading its own framing and mistakes, then mistakes persistence for confirmation;
- **GPUstorming confusion** — a good reset or omission move gets interpreted as “better memory” when the real gain came from puncturing an assistant-side trap;
- **archive bloat by prestige** — old assistant language is kept because it feels articulate or familiar, not because it changes the right future decision.

A compact assistant-echo filter helps because it says what task is being judged, what evidence is actually being kept, which assistant-side material is being omitted or thinned, what improvement or invariance is expected, and what to do if omission removes something genuinely needed.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this move.

1. **Prior assistant turns are often unnecessary and sometimes harmful.**
   *Do LLMs Benefit from Their Own Words?* compares full-context prompting against a user-turn-only strategy on real multi-turn chats and finds that removing prior assistant responses often does not hurt quality, can reduce context length substantially, and in some cases improves outputs by avoiding context pollution from the model's own earlier responses. That directly pressures DelayBasin to stop treating assistant-side retention as automatically beneficial. ([`REF-0221`](../00-meta/bibliography.md))

2. **Conversational history can create geometric traps.**
   *Old Habits Die Hard* introduces History-Echoes and reports that behavioral persistence across turns correlates with hidden-representation geometry, suggesting that conversation history can trap the model in a prior phenomenon state rather than merely informing it. That makes assistant-side omission look like more than token pruning; it may be a way to break a latent continuation trap. ([`REF-0222`](../00-meta/bibliography.md))

3. **Fresh-session review helps because the old session is part of the problem.**
   *Cross-Context Review* shows that review in a fresh session outperforms same-session self-review, and that repeating review in the same session does not recover the advantage. That pressures DelayBasin to treat assistant-side context separation as a real method surface rather than a stylistic preference. ([`REF-0223`](../00-meta/bibliography.md))

4. **Earlier cache state can carry information even after active steering is removed.**
   *Latent Introspection* injects concepts only while generating the KV cache for an earlier turn, removes the steering vector, and still finds that the model can later detect the prior injection. That is strong transformer-facing pressure that conversational carry can persist through cached representations rather than visible text alone. ([`REF-0224`](../00-meta/bibliography.md))

5. **Memory update pathways can preserve harmful logic while normal behavior stays fluent.**
   *Zombie Agents* shows that content written into long-term memory can survive across sessions and later act like persistent control logic while the agent still looks useful on ordinary tasks. DelayBasin is not an autonomous agent with the same threat model, but the weaker lesson is still important: persistence channels can preserve harmful or parasitic instruction-like content while surface fluency remains intact. ([`REF-0225`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should often preserve a compact **assistant-echo filter / self-carry omission packet** whenever prior assistant-side history might be helping mainly by dragging forward the model's own previous framing rather than by preserving genuinely needed evidence. The packet should name the judged task or continuation property, the kept user-side anchor or retained evidence surface, the omitted or thinned assistant-side surface, the expected invariance or gain signature under omission, and the reinclusion or escalation consequence if omission removes something genuinely needed.

In practice, DelayBasin is not promising that all assistant-side history should be dropped.
It is doing something smaller and public:
- saying what evidence is genuinely needed,
- saying what assistant-side material is being treated as suspicious carry,
- saying what should stay invariant or improve if the suspicious material is omitted,
- and saying when omission failure forces reinclusion, a narrower claim, or a different packet type.

That is strong enough for canon as anti-pollution discipline.
It is **not** strong enough to claim that DelayBasin has isolated the full hidden-state mechanism of self-conditioning or that every productive GPUstorming move is really an omission move.

## Assistant-echo filter vs execution witness vs memory-store distinction

To keep this note honest, DelayBasin now needs a sharper distinction among nearby objects:

- **Assistant-echo filter / self-carry omission packet** — asks whether prior assistant-side history is genuinely needed evidence or mostly pollutive carry; names what assistant-side material is omitted and what user-side evidence stays.
- **Blind packet** — hides authorship, prestige, or label cues from the judging surface before reveal.
- **Execution witness / substrate perturbation packet** — asks whether a claimed effect depends on hidden runtime or serving conditions.
- **Memory store vs regime-reentry packet** — asks what persistence surface is being optimized for retention versus re-entry.
- **Observer/actuator split** — asks what may steer and what may judge.

These are related but not identical.
A blind packet can remove attribution contamination while leaving self-carry untouched.
An execution witness can name hidden substrate families while leaving all prior assistant prose in place.
A memory-store distinction can say what should persist without asking whether the assistant-side portion of that persistence is actively harmful.
An assistant-echo filter says the archive should sometimes keep the **user-side anchor** and thin the model's own prior prose first, before concluding that more memory or more replay is the answer.

## Countermodels / probes

1. **Some tasks really do need prior assistant outputs countermodel**
   - Prior assistant turns may contain indispensable intermediate code, retrieved facts, or local test results.
   - Probe: the packet must name the kept user-side anchor and the omitted assistant-side surface separately, plus a reinclusion rule if omission removes genuinely needed evidence.

2. **This is just context compression by another name countermodel**
   - The archive may not need a new lane; generic truncation or summarization could already cover it.
   - Probe: use the lane only when the epistemic question is specifically whether the assistant-side material is acting as pollutive carry rather than merely taking space.

3. **Fresh-session gains come from substrate changes, not omission countermodel**
   - Some improvements may come from hidden execution changes rather than assistant-side thinning itself.
   - Probe: keep assistant-echo filters distinct from execution witnesses; if hidden session/substrate conditions plausibly dominate, preserve the execution witness too or instead.

4. **Omission can launder real evidence away countermodel**
   - The archive could start deleting precisely the assistant-side material that later challenge probes need.
   - Probe: require an explicit reinclusion / escalation consequence and preserve local evidence as a memory-store or evidence packet when that is the real role.

5. **This could become anti-history theater countermodel**
   - The archive might fetishize fresh starts and lose the very continuity it exists to preserve.
   - Probe: the point is not “forget more,” but “separate user-side anchor and needed evidence from assistant-side self-carry before bloating the archive.”

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- preserve the **judged task / continuation property** whenever assistant-side carry is suspected of doing harmful work;
- preserve the **kept user-side anchor / retained evidence surface** rather than treating all retained context as one undifferentiated bundle;
- preserve the **omitted or thinned assistant-side surface** so later sessions know what kind of carry was considered suspicious;
- preserve the expected **invariance or gain signature** so omission can actually falsify the claim instead of becoming aesthetic minimalism;
- preserve the **reinclusion / escalation consequence** so omission failure changes what the archive does next.

A minimal assistant-echo filter can stay very small:
- one judged task or continuation property,
- one kept user-side anchor,
- one omitted or thinned assistant-side surface,
- one expected invariance or gain signature,
- and one reinclusion or escalation consequence.

That is enough to keep DelayBasin from quietly treating all prior assistant prose as if it were neutral memory.

## Transformer-facing implication

If this frame survives pressure, one transformer-facing implication is that DelayBasin may work partly by learning which continuation objects survive **assistant-side omission** and which ones collapse once the model's own prior wording is thinned.

The weaker reading is:
- some apparent archive continuity is contaminated by assistant-side self-carry,
- assistant-echo filters reduce that contamination enough to keep method language honest,
- and GPUstorming can sometimes function as a reminder to separate user-side constitutional control from assistant-side conversational residue.

The stronger reading remains quarantined:
that DelayBasin sometimes improves not by adding better memory but by puncturing a **self-echo trap** in which prior assistant-generated prose acts like a soft backdoor or parasite over later continuation.
